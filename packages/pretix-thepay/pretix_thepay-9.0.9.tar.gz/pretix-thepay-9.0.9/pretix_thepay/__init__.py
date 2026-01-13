"""
The Pay payment provider plugin for Pretix.

This package provides integration with The Pay payment gateway for Pretix
event ticketing system.
"""
__version__ = '9.0.9'

# Import PretixPluginMeta from apps for entry point registration
from .apps import PluginApp

PretixPluginMeta = PluginApp.PretixPluginMeta

# Backward compatibility for older Pretix/Django that rely on default_app_config
default_app_config = 'pretix_thepay.apps.PluginApp'
