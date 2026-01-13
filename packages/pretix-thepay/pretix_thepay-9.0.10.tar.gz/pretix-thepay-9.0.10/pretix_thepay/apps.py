"""
The Pay payment provider plugin configuration.
"""
from django.utils.translation import gettext_lazy as _

from . import __version__

try:
    from pretix.base.plugins import PluginConfig, PLUGIN_LEVEL_EVENT
except ImportError:
    raise RuntimeError("Please use pretix 2.7.0 or above to run this plugin!")


class PluginApp(PluginConfig):
    """
    Plugin configuration for The Pay payment provider.
    
    This class registers the The Pay payment provider with Pretix and
    handles plugin initialization.
    """
    default = True
    name = 'pretix_thepay'
    verbose_name = _("The Pay")

    class PretixPluginMeta:
        name = _("The Pay")
        author = "KrisIsNew"
        version = __version__
        category = 'PAYMENT'
        level = PLUGIN_LEVEL_EVENT
        visible = True
        featured = False
        restricted = False
        description = _("This plugin allows you to receive payments via The Pay payment gateway")
        compatibility = "pretix>=2.7.0"
        settings_links = []
        navigation_links = []

    def ready(self):
        from . import signals  # NOQA
