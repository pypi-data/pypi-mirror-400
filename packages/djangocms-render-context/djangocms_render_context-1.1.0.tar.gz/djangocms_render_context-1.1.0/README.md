# DjangoCMS Render Context

The plugin for the [Django CMS](https://www.django-cms.org/) content management system.
The plugin displays the context in the template. The context can be specified directly in JSON format.
Or the context can be used as a media file. Or the context can be loaded from a URL.
The template can be entered directly or selected from a list defined in the settings in the ``DJANGOCMS_RENDER_CONTEXT_TEMPLATES`` constant.

Supported source data formats (mimetype):

 - csv (text/csv)
 - json (application/json)
 - yaml (application/yaml)
 - xml (application/xml)
 - ods (application/vnd.oasis.opendocument.spreadsheet)

## Install

Install the package from pypi.org.

```
pip install djangocms-render-context
```

Add into `INSTALLED_APPS` in your site `settings.py`:

```python
INSTALLED_APPS = [
    ...
    "easy_thumbnails",
    "filer",
    "djangocms_render_context",
]
```

### Extra settings

This value can be defined in settings.

 - `DJANGOCMS_RENDER_CONTEXT_TEMPLATES` - List of templates that the plugin can use.

For example:

```python
DJANGOCMS_RENDER_CONTEXT_TEMPLATES = (
    ("", ""),
    ("plugin.html", "Plugin"),
    ("schedule.html", "Schedule"),
)
```


## License

BSD-3-Clause
