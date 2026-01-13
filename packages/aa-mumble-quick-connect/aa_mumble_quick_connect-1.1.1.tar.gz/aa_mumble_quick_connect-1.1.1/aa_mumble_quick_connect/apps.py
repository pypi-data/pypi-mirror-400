"""
App Configuration
"""

# Django
from django.apps import AppConfig
from django.utils.text import format_lazy

# AA Mumble Quick Connect
from aa_mumble_quick_connect import __title_translated__, __version__


class AaMumbleQuickConnectConfig(AppConfig):
    """
    App configuration
    """

    name = "aa_mumble_quick_connect"
    label = "aa_mumble_quick_connect"
    verbose_name = format_lazy(
        "{app_title} v{version}", app_title=__title_translated__, version=__version__
    )
