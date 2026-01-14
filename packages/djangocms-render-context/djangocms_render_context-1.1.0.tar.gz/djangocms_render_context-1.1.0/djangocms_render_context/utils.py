from collections.abc import ValuesView
from datetime import date, datetime
from typing import Union

from django.utils.formats import localize

dataType = Union[str, dict, list, ValuesView, None]  # noqa: UP007


def get_data(data: dataType, level: int = 0) -> str:
    wrapper, separator = "{}", "\n"
    if level == 0:
        separator = "</tr>\n<tr>\n"
    if level == 1:
        wrapper = "<td>{}</td>"
    if data is None:
        content = wrapper.format("")
    elif isinstance(data, (date, datetime)):
        content = wrapper.format(localize(data))
    elif not isinstance(data, (tuple, list, dict, ValuesView)):
        content = wrapper.format(data)
    else:
        content = collect_data(data, wrapper, separator, level)
    return content


def collect_data(data: dataType, wrapper: str, separator: str, level: int) -> str:
    content = []
    if isinstance(data, (tuple, list, ValuesView)):
        for item in data:
            content.append(wrapper.format(get_data(item, level + 1)))
    elif isinstance(data, dict):
        if "href" in data and "text" in data:
            href, text = data.pop("href"), data.pop("text")
            content.append(f"""<a href="{href}">{text}</a>""")
        if "p" in data:
            para = data.pop("p")
            content.append(f"""<p>{para}</p>""")
        content.append(wrapper.format(get_data(data.values(), level + 1)))
    else:
        content.append(wrapper.format(get_data(data, level + 1)))
    return separator.join(content)


def create_html(data: dataType) -> str:
    return f"""<table class="rc-data"><tbody><tr>{get_data(data)}</tr></tbody></table>"""
