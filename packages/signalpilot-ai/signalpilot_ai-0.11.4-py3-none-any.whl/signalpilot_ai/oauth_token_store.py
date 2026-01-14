"""
OAuth Token Store - Secure storage for OAuth tokens in .env format
Stores tokens at <cache_dir>/connect/.env
(e.g., ~/Library/Caches/SignalPilotAI/connect/.env on macOS)
"""

import logging
from typing import Any, Dict, Optional

from .signalpilot_home import get_signalpilot_home

logger = logging.getLogger(__name__)


class OAuthTokenStore:
    """
    Secure storage for OAuth tokens using .env format.
    Tokens are stored with server-id prefixes for namespacing.
    """

    _instance = None

    def __init__(self):
        self._home_manager = get_signalpilot_home()

    @classmethod
    def get_instance(cls) -> 'OAuthTokenStore':
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = OAuthTokenStore()
        return cls._instance

    def store_tokens(self, integration_id: str, mcp_server_id: str, env_vars: Dict[str, str]):
        """
        Store OAuth tokens for an integration.

        Args:
            integration_id: The integration ID (e.g., 'notion', 'slack')
            mcp_server_id: The MCP server ID associated with this integration
            env_vars: Environment variables containing tokens
        """
        # Store the registry entry (mapping server_id -> integration_id)
        self._home_manager.set_oauth_registry_entry(mcp_server_id, integration_id)

        # Store the actual tokens
        self._home_manager.set_oauth_tokens(mcp_server_id, env_vars)

        logger.info(f"[OAuthTokenStore] Stored tokens for {mcp_server_id}")

    def get_tokens(self, mcp_server_id: str) -> Optional[Dict[str, str]]:
        """
        Get OAuth tokens for an MCP server.

        Args:
            mcp_server_id: The MCP server ID

        Returns:
            Environment variables dict or None if not found
        """
        return self._home_manager.get_oauth_tokens(mcp_server_id)

    def get_integration_id(self, mcp_server_id: str) -> Optional[str]:
        """
        Get the integration ID for an MCP server.

        Args:
            mcp_server_id: The MCP server ID

        Returns:
            Integration ID or None if not found
        """
        registry = self._home_manager.get_oauth_registry()
        return registry.get(mcp_server_id)

    def is_oauth_server(self, mcp_server_id: str) -> bool:
        """
        Check if an MCP server is an OAuth integration.

        Args:
            mcp_server_id: The MCP server ID

        Returns:
            True if this server has stored OAuth tokens
        """
        registry = self._home_manager.get_oauth_registry()
        return mcp_server_id in registry

    def remove_tokens(self, mcp_server_id: str) -> bool:
        """
        Remove OAuth tokens for an MCP server.

        Args:
            mcp_server_id: The MCP server ID

        Returns:
            True if tokens were removed, False if not found
        """
        # Remove from registry
        self._home_manager.remove_oauth_registry_entry(mcp_server_id)

        # Remove the tokens
        result = self._home_manager.remove_oauth_tokens(mcp_server_id)

        if result:
            logger.info(f"[OAuthTokenStore] Removed tokens for {mcp_server_id}")

        return result

    def update_tokens(self, mcp_server_id: str, env_vars: Dict[str, str]) -> bool:
        """
        Update OAuth tokens for an existing MCP server.

        Args:
            mcp_server_id: The MCP server ID
            env_vars: New environment variables containing tokens

        Returns:
            True if tokens were updated, False if server not found
        """
        if not self.is_oauth_server(mcp_server_id):
            logger.warning(f"[OAuthTokenStore] Server {mcp_server_id} not found for update")
            return False

        result = self._home_manager.set_oauth_tokens(mcp_server_id, env_vars)
        if result:
            logger.info(f"[OAuthTokenStore] Updated tokens for {mcp_server_id}")
        return result

    def get_all_oauth_servers(self) -> Dict[str, str]:
        """
        Get mapping of all OAuth MCP server IDs to their integration IDs.

        Returns:
            Dict mapping mcp_server_id -> integration_id
        """
        return self._home_manager.get_oauth_registry()


def get_oauth_token_store() -> OAuthTokenStore:
    """Get the singleton instance of the OAuth token store."""
    return OAuthTokenStore.get_instance()
