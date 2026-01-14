import logging

from cms.models.pluginmodel import CMSPlugin
from django.db import models
from django.utils.translation import gettext_lazy as _
from filer.fields.file import FilerFileField

from .exceptions import SourceParseFailure
from .loaders import LOADERS, get_cached_data_from_url, get_data_from_file, value_to_bytes

LOGGER = logging.getLogger(__name__)


class RenderContext(CMSPlugin):
    mimetype = models.CharField(
        verbose_name=_("Type of Data for context"),
        max_length=255,
        default="application/json",
        help_text=_("The format must be consistent with the data in the context."),
    )
    context = models.TextField(
        verbose_name=_("Data for context"),
        null=True,
        blank=True,
        help_text=_("Context data in selected format. They take precedence over the source file and source URL."),
    )
    file = FilerFileField(
        verbose_name=_("Source file"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text=_(
            "Context data file. If Data is specified for the context, the source file is not used even "
            "though it is specified."
        ),
    )
    source = models.URLField(
        verbose_name=_("Source URL"),
        null=True,
        blank=True,
        help_text=_(
            "The URL of the source from which the data will be downloaded. If Data for Context or Source File"
            " is specified, the source URL is not used even though it is specified."
        ),
    )
    cached = models.PositiveSmallIntegerField(
        verbose_name=_("Download period from source URL"),
        default=5,
        help_text=_(
            "The time in minutes during which data will not be retrieved from the Source URL, but will remain "
            "in the cache. If set to zero, data from the source URL is not cached, but is loaded every time."
        ),
    )

    template = models.TextField(
        verbose_name=_("Template"),
        null=True,
        blank=True,
        help_text=_("Django template for the context. It takes precedence over the template selected from the list."),
    )
    template_list = models.CharField(
        verbose_name=_("Template list"),
        null=True,
        blank=True,
        max_length=255,
        help_text=_("List of templates. If Template is specified, the template set in the list will not be used."),
    )

    def __str__(self):
        text = []
        if self.context:
            text.append(self._meta.get_field("context").verbose_name)
        elif self.file:
            text.append(self._meta.get_field("file").verbose_name)
        elif self.source:
            text.append(self._meta.get_field("source").verbose_name)
        else:
            text.append(_("Data not entered."))
        if self.template:
            text.append(self._meta.get_field("template").verbose_name)
        elif self.template_list:
            text.append(self._meta.get_field("template_list").verbose_name)
        else:
            text.append(_("No template."))
        return " + ".join([str(t) for t in text])

    def get_data(self):
        if self.context:
            return LOADERS[self.mimetype](value_to_bytes(self.context, self.mimetype))
        elif self.file:
            try:
                return get_data_from_file(self.file)
            except SourceParseFailure as err:
                LOGGER.error(err)
        elif self.source:
            try:
                return get_cached_data_from_url(self.pk, self.source, self.cached)
            except SourceParseFailure as err:
                LOGGER.error(err)
        return None
