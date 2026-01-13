"""
Template tags for the aa-mumble-quick-connect app.
"""

# Django
from django import template
from django.contrib.auth.models import User

register = template.Library()


@register.simple_tag
def aa_mumble_quick_connect_link(channel_url: str, user: User) -> str:
    """
    Generate a Mumble quick connect link with the user's Mumble username.

    :param channel_url: The base Mumble channel URL.
    :type channel_url: str
    :param user: The Django user object.
    :type user: User
    :return: The Mumble quick connect link with the user's username.
    :rtype: str
    """

    try:
        # Add the user's Mumble username to the channel URL.
        return channel_url.replace("mumble://", f"mumble://{user.mumble.username}@")
    except AttributeError:
        # If the user does not have a Mumble username or the channel URL is invalid, return the original URL.
        return channel_url
