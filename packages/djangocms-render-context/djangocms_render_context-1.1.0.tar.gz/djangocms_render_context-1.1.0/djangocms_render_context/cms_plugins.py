from cms.models.placeholdermodel import Placeholder
from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.template import Template
from django.template.backends.django import Template as DjangoTemplate
from django.template.loader import get_template
from django.utils.translation import gettext_lazy as _

from .forms import RenderContextForm
from .models import RenderContext
from .utils import create_html


@plugin_pool.register_plugin
class RenderContextPlugin(CMSPluginBase):
    model = RenderContext
    form = RenderContextForm
    name = _("Render Context Plugin")
    fieldsets = [
        (
            _("Sources"),
            {
                "fields": (
                    "mimetype",
                    "context",
                    "file",
                    (
                        "source",
                        "cached",
                    ),
                ),
            },
        ),
        (
            _("Templates"),
            {
                "classes": ["collapse"],
                "fields": (
                    "template",
                    "template_list",
                ),
            },
        ),
    ]

    def get_render_template(self, context: dict, instance: RenderContext, placeholder: Placeholder) -> DjangoTemplate:
        context["data"] = instance.get_data()
        if instance.template_list and not instance.template:
            return get_template(instance.template_list)
        tmpl = Template(instance.template if instance.template else create_html(context["data"]))
        return DjangoTemplate(tmpl, tmpl)
