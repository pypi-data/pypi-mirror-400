from collections.abc import Callable
from typing import Union

from django import forms
from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.forms import ALL_FIELDS, ModelForm
from django.template import Context, Template, TemplateDoesNotExist
from django.template.exceptions import TemplateSyntaxError
from django.template.loader import get_template
from django.utils.translation import gettext_lazy as _
from filer.models.filemodels import File
from sekizai.context import SekizaiContext

from .cache import get_cache_key
from .exceptions import SourceParseFailure
from .loaders import (
    CONTEXT_DATA_FORMATS,
    LOADERS,
    SUPPORTED_FILE_TYPES,
    get_data_from_file,
    get_data_from_url,
    value_to_bytes,
)

TEMPLATES = (("", ""),)

sourceType = Union[str, File]  # noqa: UP007


class RenderContextForm(ModelForm):
    """Render Context Form."""

    mimetype = forms.ChoiceField(
        label=_("Type of Data for context"),
        choices=CONTEXT_DATA_FORMATS,
        help_text=_("The format must be consistent with the data in the context."),
    )
    template_list = forms.ChoiceField(
        label=_("Template list"),
        required=False,
        choices=getattr(settings, "DJANGOCMS_RENDER_CONTEXT_TEMPLATES", TEMPLATES),
        help_text=_("List of templates. If Template is specified, the template set in the list will not be used."),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["file"].help_text += " " + _("Supported formats are:") + " " + ", ".join(SUPPORTED_FILE_TYPES)

    def clean_template_list(self) -> None:
        if self.cleaned_data["template_list"]:
            try:
                get_template(self.cleaned_data["template_list"])
            except TemplateSyntaxError as error:
                raise ValidationError(error) from error
            except TemplateDoesNotExist as error:
                raise ValidationError(f'Template "{error}" does not exist.') from error
        return self.cleaned_data["template_list"]

    def check_value(self, name: str, value: sourceType, loader: Callable) -> Context:
        try:
            return Context(loader(value))
        except SourceParseFailure as error:
            self.add_error(name, error)

    def check_context_data(self, value: str, mimetype: str) -> Context:
        try:
            return Context(LOADERS[mimetype](value_to_bytes(value, mimetype)))
        except SourceParseFailure as error:
            self.add_error("context", error)

    def check_context(self, cleaned_data: dict) -> Context:
        context = Context({})
        if cleaned_data["context"]:
            context = self.check_context_data(cleaned_data["context"], cleaned_data["mimetype"])
        elif cleaned_data["file"]:
            context = self.check_value("file", cleaned_data["file"], get_data_from_file)
        elif cleaned_data["source"]:
            context = self.check_value("source", cleaned_data["source"], get_data_from_url)
        if context is None:
            self.add_error(ALL_FIELDS, "Failed to set context.")
            context = Context({})
        return context

    def check_template(self, cleaned_data: dict, context: Context) -> None:
        template = None
        field_name = ALL_FIELDS
        if cleaned_data["template"]:
            field_name = "template"
            try:
                template = Template(cleaned_data["template"])
            except TemplateSyntaxError as error:
                self.add_error("template", error)
        elif cleaned_data["template_list"]:
            field_name = "template_list"
            template = get_template(cleaned_data["template_list"]).template
        if template:
            try:
                template.render(SekizaiContext(context))
            except (TemplateDoesNotExist, TemplateSyntaxError) as error:
                self.add_error(field_name, error)

    def clean(self) -> None:
        """Clean form."""
        cleaned_data = super().clean()
        if self.is_valid():
            context = self.check_context(cleaned_data)
            self.check_template(cleaned_data, context)

    def save(self, *args, **kwargs):
        if self.instance.pk:
            cache.delete(get_cache_key(self.instance.pk))
        return super().save(*args, **kwargs)
