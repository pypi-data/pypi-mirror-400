"""
GPWebPay payment provider plugin for Pretix.

This package provides integration with GPWebPay payment gateway for Pretix
event ticketing system.
"""
try:
    from pretix.base.plugins import PluginConfig, PLUGIN_LEVEL_EVENT
except ImportError:
    raise RuntimeError("Please use pretix 4.0.0 or above to run this plugin!")
from django.utils.translation import gettext_lazy as _

__version__ = '1.0.1'


class GPWebPayApp(PluginConfig):
    """
    Plugin configuration for GPWebPay payment provider.
    
    This class registers the GPWebPay payment provider with Pretix and
    handles plugin initialization.
    """
    name = 'pretix_gpwebpay'
    verbose_name = _("GPWebPay")

    class PretixPluginMeta:
        name = _("GPWebPay")
        author = "KrisIsNew"
        version = __version__
        category = 'PAYMENT'
        level = PLUGIN_LEVEL_EVENT
        visible = True
        featured = False
        restricted = False
        description = _("This plugin allows you to receive payments via GPWebPay payment gateway")
        compatibility = "pretix>=4.0.0"
        settings_links = []
        navigation_links = []

    def ready(self):
        from . import signals  # NOQA


# Create alias for entry point registration
PretixPluginMeta = GPWebPayApp.PretixPluginMeta

default_app_config = 'pretix_gpwebpay.GPWebPayApp'

