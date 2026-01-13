"""
GPWebPay payment provider plugin for Pretix.

This package provides integration with GPWebPay payment gateway for Pretix
event ticketing system.
"""
from pretix.base.plugins import PluginConfig

__version__ = '1.0.0'


class PretixPluginMeta(PluginConfig):
    """
    Plugin configuration for GPWebPay payment provider.
    
    This class registers the GPWebPay payment provider with Pretix and
    handles plugin initialization.
    """
    name = 'pretix_gpwebpay'
    verbose_name = 'GPWebPay'
    author = 'KrisIsNew'
    description = 'GPWebPay payment provider for Pretix'
    visible = True
    version = __version__
    category = 'PAYMENT'
    compatibility = "pretix>=4.0.0"

    def ready(self):
        from . import signals  # NOQA

