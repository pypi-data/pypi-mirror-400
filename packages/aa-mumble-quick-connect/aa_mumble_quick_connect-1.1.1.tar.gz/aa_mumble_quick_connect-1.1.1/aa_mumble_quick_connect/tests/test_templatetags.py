"""
Test the apps' template tags
"""

# Standard Library
from unittest.mock import Mock

# Django
from django.contrib.auth.models import User

# AA Mumble Quick Connect
from aa_mumble_quick_connect.templatetags.aa_mumble_quick_connect import (
    aa_mumble_quick_connect_link,
)
from aa_mumble_quick_connect.tests import BaseTestCase


class TestQuickConnectLinkTemplateTag(BaseTestCase):
    """
    Test aa_mumble_quick_connect template tag
    """

    def test_creates_link_with_valid_channel_url_and_user(self):
        """
        Test that the function creates a link with valid channel_url and user

        :return:
        :rtype:
        """

        user = Mock(spec=User)
        user.mumble.username = "mumbleuser"
        channel_url = "mumble://example.com/room"

        result = aa_mumble_quick_connect_link(channel_url, user)

        self.assertEqual(result, "mumble://mumbleuser@example.com/room")

    def test_returns_none_if_channel_url_is_none(self):
        """
        Test that the function returns None if channel_url is None

        :return:
        :rtype:
        """

        user = Mock(spec=User)
        user.mumble.username = "mumbleuser"

        result = aa_mumble_quick_connect_link(None, user)

        self.assertIsNone(result)

    def test_returns_original_url_if_user_has_no_mumble(self):
        """
        Test that the function returns the original URL if user has no mumble attribute

        :return:
        :rtype:
        """

        user = Mock(spec=User)

        del user.mumble  # Remove the attribute to simulate absence

        channel_url = "mumble://example.com/room"
        result = aa_mumble_quick_connect_link(channel_url, user)

        self.assertEqual(result, channel_url)

    def test_returns_original_url_if_user_is_none(self):
        """
        Test that the function returns the original URL if user is None

        :return:
        :rtype:
        """

        channel_url = "mumble://example.com/room"
        result = aa_mumble_quick_connect_link(channel_url, None)

        self.assertEqual(result, channel_url)

    def test_returns_original_url_if_channel_url_does_not_contain_mumble_prefix(self):
        """
        Test that the function returns the original URL if channel_url does not contain mumble:// prefix

        :return:
        :rtype:
        """

        user = Mock(spec=User)
        user.mumble.username = "mumbleuser"
        channel_url = "https://example.com/room"

        result = aa_mumble_quick_connect_link(channel_url, user)

        self.assertEqual(result, channel_url)
