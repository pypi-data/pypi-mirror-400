"""
Configuration Manager for Confluence Assistant Skills

Handles configuration from multiple sources with priority:
1. Environment variables (highest priority)
2. settings.local.json (personal, gitignored)
3. settings.json (team defaults, committed)
4. Built-in defaults (lowest priority)

Environment Variables:
    CONFLUENCE_API_TOKEN - API token for authentication
    CONFLUENCE_EMAIL - Email address for authentication
    CONFLUENCE_SITE_URL - Confluence site URL (e.g., https://your-site.atlassian.net)
    CONFLUENCE_PROFILE - Profile name to use (default: "default")

Usage:
    from confluence_assistant_skills_lib import get_confluence_client, get_config

    # Get a configured client
    client = get_confluence_client(profile="production")

    # Get raw configuration
    config = get_config()
"""

import os
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any, TYPE_CHECKING

from assistant_skills_lib.config_manager import BaseConfigManager
from assistant_skills_lib.error_handler import ValidationError

if TYPE_CHECKING:
    from .confluence_client import ConfluenceClient

logger = logging.getLogger(__name__)


class ConfigManager(BaseConfigManager):
    """
    Manages Confluence configuration from multiple sources, inheriting from BaseConfigManager.
    """

    def __init__(self, profile: Optional[str] = None):
        """
        Initialize the configuration manager.

        Args:
            profile: Profile name to use. If not provided,
                       searches for default from env or settings files.
        """
        super().__init__(profile=profile)

    def get_service_name(self) -> str:
        """Returns the name of the service, which is 'confluence'."""
        return "confluence"

    def get_default_config(self) -> Dict[str, Any]:
        """Returns the default configuration dictionary for Confluence."""
        return {
            "api": {
                "version": "2",
                "timeout": 30,
                "max_retries": 3,
                "retry_backoff": 2.0,
                "verify_ssl": True,
            },
            "default_profile": "default",
            "profiles": {},
        }





    def get_credentials(self, profile: Optional[str] = None) -> Dict[str, Any]:
        """
        Get and validate credentials for a specific profile.

        Args:
            profile: Profile name. If None, uses default profile.

        Returns:
            A dictionary containing validated 'url', 'email', and 'api_token'.

        Raises:
            ValidationError: If required credentials are not found or are invalid.
        """
        profile_name = profile or self.profile
        profile_config = self.get_profile_config(profile_name)

        url = self.get_credential_from_env('SITE_URL') or profile_config.get('url')
        email = self.get_credential_from_env('EMAIL') or profile_config.get('email')
        api_token = self.get_credential_from_env('API_TOKEN') or profile_config.get('api_token')

        if not url:
            raise ValidationError(
                f"Confluence URL not configured for profile '{profile_name}'. "
                "Set CONFLUENCE_SITE_URL or configure in .claude/settings.json."
            )
        if not email:
            raise ValidationError(
                f"Confluence email not configured for profile '{profile_name}'. "
                "Set CONFLUENCE_EMAIL or configure in .claude/settings.json."
            )
        if not api_token:
            raise ValidationError(
                f"Confluence API token not configured for profile '{profile_name}'. "
                "Set CONFLUENCE_API_TOKEN or configure in .claude/settings.json."
            )

        # Assuming validate_url and validate_email will be imported from base validators
        from assistant_skills_lib.validators import validate_url, validate_email
        return {
            "url": validate_url(url, require_https=True),
            "email": validate_email(email),
            "api_token": api_token,
        }

# Module-level convenience functions

def get_confluence_client(
    profile: Optional[str] = None,
    **kwargs
) -> "ConfluenceClient":
    """
    Get a configured Confluence client.

    Args:
        profile: Profile name to use.
        **kwargs: Additional arguments passed to ConfluenceClient.

    Returns:
        Configured ConfluenceClient instance.
    """
    from .confluence_client import ConfluenceClient

    manager = ConfigManager.get_instance(profile=profile)
    
    # Get credentials and API settings from the manager
    credentials = manager.get_credentials()
    api_config = manager.get_api_config()

    client_kwargs = {
        "base_url": credentials["url"],
        "email": credentials["email"],
        "api_token": credentials["api_token"],
        "timeout": api_config.get("timeout", 30),
        "max_retries": api_config.get("max_retries", 3),
        "retry_backoff": api_config.get("retry_backoff", 2.0),
        "verify_ssl": api_config.get("verify_ssl", True),
    }
    client_kwargs.update(kwargs)

    return ConfluenceClient(**client_kwargs)


def get_default_space(profile: Optional[str] = None) -> Optional[str]:
    """
    Get the default space key from configuration.
    """
    manager = ConfigManager.get_instance(profile=profile)
    profile_config = manager.get_profile_config()
    return profile_config.get("default_space")


def get_space_keys(profile: Optional[str] = None) -> list:
    """
    Get the list of configured space keys.
    """
    manager = ConfigManager.get_instance(profile=profile)
    profile_config = manager.get_profile_config()
    return profile_config.get("space_keys", [])
