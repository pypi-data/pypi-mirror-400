import base64
import binascii
import csv
import json
import xml.etree.ElementTree as ET
import zipfile
from io import BytesIO, StringIO
from mimetypes import guess_type
from typing import Union, cast

import requests
import yaml
from django.conf import settings
from django.core.cache import cache
from django.utils.translation import gettext_lazy as _
from filer.models.filemodels import File

# Use the C (faster) implementation if possible
try:
    from yaml import CSafeLoader as SafeLoader
except ImportError:  # pragma: no cover
    from yaml import SafeLoader  # type: ignore

from .cache import get_cache_key
from .exceptions import SourceParseFailure

dataType = Union[dict, list]  # noqa: UP007
valueType = Union[str, list]  # noqa: UP007
cellType = Union[dict, str, list]  # noqa: UP007
nodeTextType = Union[str, None]  # noqa: UP007
payloadType = Union[str, dict]  # noqa: UP007


def get_mime_type_message(mime_type: nodeTextType) -> str:
    return (
        _("Unsupported file mime type: ")
        + str(mime_type)
        + ". "
        + _("Only allowed are:")
        + " "
        + ", ".join(SUPPORTED_FILE_TYPES)
        + "."
    )


def get_data_from_file(source: File) -> dataType:
    if source.mime_type not in LOADERS:
        raise SourceParseFailure(get_mime_type_message(source.mime_type))
    return LOADERS[source.mime_type](source.file.read())


def value_to_bytes(value: str, mimetype: str) -> bytes:
    if mimetype == "application/vnd.oasis.opendocument.spreadsheet":
        try:
            content = base64.b64decode(value)
        except (binascii.Error, ValueError) as err:
            raise SourceParseFailure(err) from err
    else:
        content = value.encode("utf8")
    return content


def load_json(content: bytes) -> dataType:
    try:
        return json.load(BytesIO(content))
    except json.decoder.JSONDecodeError as err:
        raise SourceParseFailure(err) from err


def load_yaml(content: bytes) -> dataType:
    try:
        return yaml.load(content, Loader=SafeLoader)
    except yaml.YAMLError as err:
        raise SourceParseFailure(err) from err


def load_csv(content: bytes) -> list:
    try:
        body = content.decode("utf8")
    except UnicodeDecodeError as err:
        raise SourceParseFailure(err) from err
    reader = csv.reader(StringIO(body))
    try:
        return list(reader)
    except csv.Error as err:
        raise SourceParseFailure(err) from err


def load_xml(content: bytes) -> dataType:
    data = []
    try:
        doc = ET.parse(BytesIO(content))
    except ET.ParseError as err:
        raise SourceParseFailure(err) from err
    root = doc.getroot()
    for row in root:
        data.append([column.text for column in row])
    return data


def load_spreadsheet(content: bytes) -> dataType:
    handle = None
    try:
        handle = zipfile.ZipFile(BytesIO(content))
        payload = handle.read("content.xml")
    except (zipfile.BadZipFile, KeyError, ValueError) as err:
        raise SourceParseFailure(err) from err
    finally:
        if handle is None:
            pass
        else:
            handle.close()
    try:
        doc = ET.parse(BytesIO(payload))
    except ET.ParseError as err:
        raise SourceParseFailure(err) from err
    return pase_data(cast(ET.ElementTree, doc))


def pase_data(doc: ET.ElementTree) -> dataType:
    data: list[list[cellType]] = []
    ns = {
        "table": "urn:oasis:names:tc:opendocument:xmlns:table:1.0",
        "text": "urn:oasis:names:tc:opendocument:xmlns:text:1.0",
        "xlink": "http://www.w3.org/1999/xlink",
    }
    max_gap = getattr(settings, "DJANGOCMS_RENDER_CONTEXT_ODS_MAX_GAP", 51)
    root = doc.getroot()
    if root is None:
        return data
    table = root.find(".//table:table", ns)
    if table is not None:
        for row in table.findall("table:table-row", ns):
            repeated = row.get(qname(ns, "table:number-rows-repeated"))
            if repeated is not None:
                offset = int(repeated) - 1
                if offset < max_gap:
                    data.extend([] * offset)
            data.append(parse_cells(ns, max_gap, row))
    while data and data[-1] == [""]:
        data.pop()
    return data


def parse_cells(ns: dict[str, str], max_gap: int, row: ET.Element) -> list[cellType]:
    line: list[cellType] = []
    for cell in row.findall("table:table-cell", ns):
        repeated = cell.get(qname(ns, "table:number-columns-repeated"))
        if repeated is not None:
            offset = int(repeated) - 1
            if offset < max_gap:
                line.extend([""] * offset)
        payload: list[payloadType] = []
        for text in cell.findall("text:p", ns):
            if text.text is not None:
                payload.append({"p": text.text})
            for link in text.findall("text:a", ns):
                href = link.get(qname(ns, "xlink:href"))
                payload.append({"href": href, "text": none_to_str(link.text)})
        if len(payload) == 1:
            payload = payload[0]  # type: ignore
            if "p" in payload:
                payload = payload["p"]  # type: ignore
        if payload == []:
            payload = ""  # type: ignore
        line.append(payload)
    return line


def none_to_str(value: nodeTextType) -> str:
    return "" if value is None else str(value)


def qname(ns: dict[str, str], prefix_and_name: str) -> str:
    """Create qualified xml element name."""
    parts = prefix_and_name.split(":", 1)
    prefix, name = parts
    return str(ET.QName(ns[prefix], name))


def load_source(url: str):
    """Load data from the source."""
    timeout = getattr(settings, "DJANGOCMS_RENDER_CONTEXT_LOAD_TIMEOUT", 6)
    verify = getattr(settings, "DJANGOCMS_RENDER_CONTEXT_VERIFY", True)
    response = requests.get(url, timeout=timeout, verify=verify)
    response.raise_for_status()
    return response


def get_data_from_url(source: str) -> dataType:
    data: dataType = []
    try:
        response = load_source(source)
    except requests.RequestException as err:
        raise SourceParseFailure(err) from err
    content_type = response.headers.get("Content-Type")
    if content_type not in LOADERS:
        content_type = guess_type(source)[0]
    if content_type not in LOADERS:
        raise SourceParseFailure(get_mime_type_message(content_type))
    try:
        data = LOADERS[content_type](response.content)
    except SourceParseFailure as err:
        raise SourceParseFailure(_("Resource parsing failed.")) from err
    return data


def get_cached_data_from_url(identifier: int, source: str, timeout: int) -> dataType:
    key = get_cache_key(identifier)
    if timeout:
        data = cache.get(key)
        if data is None:
            data = get_data_from_url(source)
            cache.set(key, data, timeout * 60)
    else:
        data = get_data_from_url(source)
    return data


SUPPORTED_FILE_TYPES = ("csv", "json", "yaml", "xml", "ods")
LOADERS = {
    "text/csv": load_csv,
    "application/json": load_json,
    "application/yaml": load_yaml,
    "application/xml": load_xml,
    "application/vnd.oasis.opendocument.spreadsheet": load_spreadsheet,
}
CONTEXT_DATA_FORMATS = (
    ("application/json", "JSON"),
    ("application/yaml", "YAML"),
    ("application/xml", "XML"),
    ("text/csv", "CSV"),
    ("application/vnd.oasis.opendocument.spreadsheet", "ODS (in Base64)"),
)
