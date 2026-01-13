from django.conf import settings
from django.utils.translation import gettext_lazy as _

from django_dash._helpers import ASSET_PATH

# Define defaults for DASH_SETTINGS
DEFAULT_DASH_SETTINGS = {
   "SITE_TITLE": "Django Admin",
    "SITE_HEADER": "Administration",
    "INDEX_TITLE": "hi, welcome to your dashboard",
    "SITE_LOGO": f"{ASSET_PATH}admin/img/daisyui-logomark.svg",
    "EXTRA_STYLES": [],
    "EXTRA_SCRIPTS": [],
    "LOAD_FULL_STYLES": False,
    "SHOW_CHANGELIST_FILTER": False,
    "DONT_SUPPORT_ME": False,
    "SIDEBAR_FOOTNOTE": "",
    "FORM_RENDERER": "django.forms.renderers.TemplatesSetting",
    "X_FRAME_OPTIONS": "SAMEORIGIN",
    "DEFAULT_THEME": 'None',
    "DEFAULT_THEME_DARK": None,
    "SHOW_THEME_SELECTOR": True,
    "LIST_PER_PAGE": 20,
    "THEME_LIST": [
        {"name": _("Light"), "value": "light"},
        {"name": _("Dark"), "value": "dark"},
        {"name": _("CMYK"), "value": "cmyk"},
        {"name": _("Dracula"), "value": "dracula"},
        {"name": _("Lemonade"), "value": "lemonade"},
        {"name": _("Halloween"), "value": "halloween"},
        {"name": _("Garden"), "value": "garden"},
    ],
    "APPS_REORDER": {
        "auth": {
            "icon": "fa-solid fa-person-military-pointing",
            "name": _("Authentication"),
            "hide": False,
            "app": "users",
            # 'priority': 1,  # higher value will appear on top items
        },
    },
}

# Get DASH_SETTINGS from settings.py or fall back to defaults
DASH_SETTINGS = getattr(settings, "DASH_SETTINGS", DEFAULT_DASH_SETTINGS)

# Ensure any missing keys from defaults are included
for key, value in DEFAULT_DASH_SETTINGS.items():
    DASH_SETTINGS.setdefault(key, value)

settings.FORM_RENDERER = DASH_SETTINGS["FORM_RENDERER"]

settings.X_FRAME_OPTIONS = DASH_SETTINGS["X_FRAME_OPTIONS"]
