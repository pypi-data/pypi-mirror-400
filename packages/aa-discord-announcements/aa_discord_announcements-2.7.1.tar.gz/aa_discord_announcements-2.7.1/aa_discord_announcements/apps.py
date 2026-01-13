"""
App config
"""

# Django
from django.apps import AppConfig
from django.utils.text import format_lazy

# AA Discord Announcements
from aa_discord_announcements import __title_translated__, __version__


class AaDiscordAnnouncementsConfig(AppConfig):
    """
    Application config
    """

    name = "aa_discord_announcements"
    label = "aa_discord_announcements"
    verbose_name = format_lazy(
        "{app_title} v{version}", app_title=__title_translated__, version=__version__
    )
