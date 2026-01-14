"""
Composio Integration Service
Manages OAuth integrations via Cloudflare Worker and creates MCP server configurations.
"""

import asyncio
import hashlib
import json
import logging
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import aiohttp

from .cache_service import CacheDirectoryManager, RobustFileOperations
from .integrations_config import (
    get_integration_config,
    get_all_integration_ids,
    get_integration_info_for_frontend,
    get_mcp_server_config,
    get_mcp_server_config_for_storage,
    build_env_from_credentials,
)
from .mcp_service import get_mcp_service
from .oauth_token_store import get_oauth_token_store

logger = logging.getLogger(__name__)

# Backend URL - set via environment variable
# Use Node.js backend (8788) for credential retrieval with Composio SDK
DEFAULT_WORKER_URL = os.environ.get(
    'COMPOSIO_WORKER_URL',
    'https://oauth.signalpilot.ai'  # Node.js backend with Composio SDK
)

# Token refresh interval in seconds (15 minutes)
TOKEN_REFRESH_INTERVAL_SECONDS = 15 * 60


class ComposioIntegrationService:
    """Service for managing Composio OAuth integrations."""

    _instance = None

    def __init__(self):
        self._worker_url: str = DEFAULT_WORKER_URL
        self._user_id: Optional[str] = None
        self._integrations_file: Optional[Path] = None
        self._refresh_task: Optional[asyncio.Task] = None
        self._setup_storage()

    @classmethod
    def get_instance(cls) -> 'ComposioIntegrationService':
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = ComposioIntegrationService()
        return cls._instance

    def _setup_storage(self):
        """Set up storage for integration state."""
        cache_dir = CacheDirectoryManager.find_usable_cache_directory()
        if cache_dir:
            self._integrations_file = cache_dir / 'composio_integrations.json'
            logger.debug(f"[Composio] Using integrations file: {self._integrations_file}")
        else:
            logger.warning("[Composio] No usable cache directory found")

    def _get_user_id(self) -> str:
        """Get or create a unique user ID for this installation."""
        if self._user_id:
            return self._user_id

        # Try to load from storage
        state = self._load_state()
        if 'user_id' in state and state['user_id']:
            self._user_id = state['user_id']
        else:
            # Generate new user ID
            self._user_id = str(uuid.uuid4())
            state['user_id'] = self._user_id
            self._save_state(state)

        return self._user_id

    def _load_state(self) -> Dict[str, Any]:
        """Load integration state from file."""
        if not self._integrations_file or not self._integrations_file.exists():
            return {'user_id': None, 'connections': {}}

        try:
            with open(self._integrations_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"[Composio] Error loading state: {e}")
            return {'user_id': None, 'connections': {}}

    def _save_state(self, state: Dict[str, Any]):
        """Save integration state to file."""
        if not self._integrations_file:
            logger.warning("[Composio] No integrations file configured")
            return

        try:
            RobustFileOperations.safe_write_json(self._integrations_file, state)
            logger.debug("[Composio] State saved successfully")
        except Exception as e:
            logger.error(f"[Composio] Error saving state: {e}")

    def _compute_credentials_hash(self, credentials: Dict[str, Any]) -> str:
        """Compute a hash of credentials for change detection."""
        # Use access_token as the primary indicator of credential changes
        token = credentials.get('access_token', '')
        if not token:
            # Fallback to hashing all credential values
            token = json.dumps(credentials, sort_keys=True)
        return hashlib.sha256(token.encode()).hexdigest()[:16]

    def _has_connected_integrations(self) -> bool:
        """Check if there are any connected integrations."""
        state = self._load_state()
        connections = state.get('connections', {})
        return any(
            conn.get('status') == 'connected'
            for conn in connections.values()
        )

    def _start_refresh_task(self):
        """Start the background token refresh task if not already running."""
        if self._refresh_task is not None and not self._refresh_task.done():
            logger.debug("[Composio] Refresh task already running")
            return

        try:
            loop = asyncio.get_event_loop()
            self._refresh_task = loop.create_task(self._refresh_loop())
            logger.info("[Composio] Started background token refresh task")
        except RuntimeError:
            logger.warning("[Composio] No event loop available, refresh task not started")

    def _stop_refresh_task(self):
        """Stop the background token refresh task."""
        if self._refresh_task is not None and not self._refresh_task.done():
            self._refresh_task.cancel()
            logger.info("[Composio] Stopped background token refresh task")
        self._refresh_task = None

    async def _refresh_loop(self):
        """Background loop that periodically refreshes tokens for all connected integrations."""
        logger.info(f"[Composio] Token refresh loop started (interval: {TOKEN_REFRESH_INTERVAL_SECONDS}s)")

        while True:
            try:
                await asyncio.sleep(TOKEN_REFRESH_INTERVAL_SECONDS)

                # Check if there are still connected integrations
                if not self._has_connected_integrations():
                    logger.info("[Composio] No connected integrations, stopping refresh loop")
                    break

                # Refresh tokens for all connected integrations
                state = self._load_state()
                connections = state.get('connections', {})

                for integration_id, connection in connections.items():
                    if connection.get('status') != 'connected':
                        continue

                    try:
                        result = await self.refresh_token(integration_id)
                        if result.get('tokens_updated'):
                            logger.info(f"[Composio] Tokens updated for {integration_id}")
                        else:
                            logger.debug(f"[Composio] Tokens unchanged for {integration_id}")
                    except Exception as e:
                        logger.warning(f"[Composio] Failed to refresh {integration_id}: {e}")

            except asyncio.CancelledError:
                logger.info("[Composio] Refresh loop cancelled")
                break
            except Exception as e:
                logger.error(f"[Composio] Error in refresh loop: {e}")
                # Continue loop despite errors

    async def refresh_token(self, integration_id: str) -> Dict[str, Any]:
        """
        Refresh tokens for an integration by fetching fresh credentials from Composio.

        Returns:
            Dict with 'success', 'tokens_updated', and optionally error info
        """
        config = get_integration_config(integration_id)
        if not config:
            raise ValueError(f"Unknown integration: {integration_id}")

        state = self._load_state()
        connection = state.get('connections', {}).get(integration_id, {})

        if connection.get('status') != 'connected':
            return {'success': False, 'error': 'Integration not connected'}

        user_id = self._get_user_id()

        # Fetch fresh credentials from Composio
        try:
            result = await self._make_worker_request(
                'POST',
                f'/credentials/{integration_id}/{user_id}'
            )
        except Exception as e:
            logger.error(f"[Composio] Failed to fetch credentials for {integration_id}: {e}")
            return {'success': False, 'error': str(e)}

        credentials = result.get('credentials', {})
        if not credentials:
            return {'success': False, 'error': 'No credentials received'}

        # Check if tokens have changed
        new_hash = self._compute_credentials_hash(credentials)
        old_hash = connection.get('credentials_hash', '')

        if new_hash == old_hash:
            # Update last_refresh timestamp even if tokens unchanged
            connection['last_refresh'] = datetime.utcnow().isoformat()
            state['connections'][integration_id] = connection
            self._save_state(state)
            return {'success': True, 'tokens_updated': False}

        logger.info(f"[Composio] Token change detected for {integration_id}")

        # Get MCP server ID from connection
        mcp_server_id = connection.get('mcp_server_id')
        if not mcp_server_id:
            return {'success': False, 'error': 'No MCP server ID found'}

        # Update tokens in secure store (NOT in mcp.json)
        token_store = get_oauth_token_store()
        env_vars = build_env_from_credentials(integration_id, credentials)
        token_store.update_tokens(mcp_server_id, env_vars)

        # Reconnect MCP server to pick up new tokens
        mcp_service = get_mcp_service()

        try:
            # Disconnect existing server
            try:
                await mcp_service.disconnect(mcp_server_id)
                logger.debug(f"[Composio] Disconnected MCP server: {mcp_server_id}")
            except Exception as e:
                logger.warning(f"[Composio] Error disconnecting MCP server: {e}")

            # Reconnect with new tokens (tokens will be injected from store)
            await mcp_service.connect(mcp_server_id)
            logger.info(f"[Composio] Reconnected MCP server {mcp_server_id} with new tokens")

        except Exception as e:
            logger.error(f"[Composio] Failed to update MCP server: {e}")
            # Still update the hash since we have new credentials
            # The MCP server may need manual intervention

        # Update state with new hash and timestamp
        connection['credentials_hash'] = new_hash
        connection['last_refresh'] = datetime.utcnow().isoformat()
        state['connections'][integration_id] = connection
        self._save_state(state)

        return {'success': True, 'tokens_updated': True}

    def is_configured(self) -> bool:
        """Check if the worker URL is properly configured."""
        return bool(self._worker_url and 'YOUR_SUBDOMAIN' not in self._worker_url)

    def get_worker_url(self) -> str:
        """Get the worker URL for frontend to call directly."""
        return self._worker_url

    async def _make_worker_request(
        self,
        method: str,
        path: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make a request to the Cloudflare Worker."""
        if not self.is_configured():
            raise ValueError("Composio worker URL not configured. Set COMPOSIO_WORKER_URL environment variable.")

        url = f"{self._worker_url}{path}"
        headers = {
            'Content-Type': 'application/json',
        }

        async with aiohttp.ClientSession() as session:
            async with session.request(
                method,
                url,
                headers=headers,
                json=data,
            ) as response:
                if not response.ok:
                    error_text = await response.text()
                    logger.error(f"[Composio] Worker error: {response.status} - {error_text}")
                    raise Exception(f"Worker request failed: {error_text}")

                return await response.json()

    def get_integrations(self) -> List[Dict[str, Any]]:
        """
        Get list of integrations with their connection status.
        Safe to expose to frontend.
        """
        integrations = get_integration_info_for_frontend()
        state = self._load_state()
        connections = state.get('connections', {})

        # Add connection status to each integration
        for integration in integrations:
            integration_id = integration['id']
            connection = connections.get(integration_id, {})
            integration['status'] = connection.get('status', 'disconnected')
            integration['mcpServerId'] = connection.get('mcp_server_id')

        return integrations

    def get_initiate_url(self, integration_id: str) -> Dict[str, str]:
        """
        Get the worker URL for initiating OAuth connection.
        Frontend will call the worker directly.

        Returns:
            Dict with 'workerUrl' and 'userId' for the frontend to use
        """
        config = get_integration_config(integration_id)
        if not config:
            raise ValueError(f"Unknown integration: {integration_id}")

        if not self.is_configured():
            raise ValueError("Composio worker URL not configured. Set COMPOSIO_WORKER_URL environment variable.")

        user_id = self._get_user_id()

        # Update state to connecting
        state = self._load_state()
        if 'connections' not in state:
            state['connections'] = {}

        state['connections'][integration_id] = {
            'status': 'connecting',
        }
        self._save_state(state)

        return {
            'workerUrl': f"{self._worker_url}/initiate/{integration_id}",
            'userId': user_id,
        }

    async def complete_connection(self, integration_id: str) -> Dict[str, Any]:
        """
        Complete OAuth connection and create MCP server.
        Called after OAuth callback is received.

        Returns:
            Dict with connection details and MCP server ID
        """
        config = get_integration_config(integration_id)
        if not config:
            raise ValueError(f"Unknown integration: {integration_id}")

        user_id = self._get_user_id()

        # Get credentials from worker
        result = await self._make_worker_request(
            'POST',
            f'/credentials/{integration_id}/{user_id}'
        )

        credentials = result.get('credentials', {})
        if not credentials:
            raise Exception(f"No credentials received for {integration_id}")

        # Create MCP server configuration WITHOUT tokens (for storage in mcp.json)
        mcp_config = get_mcp_server_config_for_storage(integration_id)
        if not mcp_config:
            raise Exception(f"Failed to create MCP config for {integration_id}")

        # Store tokens securely (NOT in mcp.json)
        token_store = get_oauth_token_store()
        env_vars = build_env_from_credentials(integration_id, credentials)
        token_store.store_tokens(integration_id, mcp_config['id'], env_vars)

        # Save MCP server config (without tokens) to mcp.json
        mcp_service = get_mcp_service()
        mcp_service.save_server_config(mcp_config)

        # Connect to the new MCP server (tokens will be injected at runtime)
        try:
            await mcp_service.connect(mcp_config['id'])
            logger.info(f"[Composio] Connected to MCP server: {mcp_config['id']}")
        except Exception as e:
            logger.warning(f"[Composio] Failed to auto-connect MCP server: {e}")

        # Update state to connected with credentials hash for refresh detection
        state = self._load_state()
        if 'connections' not in state:
            state['connections'] = {}

        state['connections'][integration_id] = {
            'status': 'connected',
            'account_id': result.get('accountId'),
            'mcp_server_id': mcp_config['id'],
            'credentials_hash': self._compute_credentials_hash(credentials),
            'last_refresh': datetime.utcnow().isoformat(),
        }
        self._save_state(state)

        # Start background refresh task if not already running
        self._start_refresh_task()

        return {
            'status': 'connected',
            'mcpServerId': mcp_config['id'],
            'mcpServerName': mcp_config['name'],
        }

    async def check_connection_status(self, integration_id: str) -> Dict[str, Any]:
        """
        Check the connection status for an integration.
        """
        config = get_integration_config(integration_id)
        if not config:
            raise ValueError(f"Unknown integration: {integration_id}")

        user_id = self._get_user_id()

        # Check status with worker
        result = await self._make_worker_request(
            'GET',
            f'/status/{user_id}'
        )

        status_info = result.get('status', {}).get(integration_id, {})
        connected = status_info.get('connected', False)

        # Update local state
        state = self._load_state()
        connection = state.get('connections', {}).get(integration_id, {})

        if connected and connection.get('status') != 'connected':
            # Connection became active, need to complete setup
            return await self.complete_connection(integration_id)

        return {
            'status': 'connected' if connected else connection.get('status', 'disconnected'),
            'mcpServerId': connection.get('mcp_server_id'),
        }

    async def disconnect(self, integration_id: str) -> Dict[str, Any]:
        """
        Disconnect an integration and remove MCP server.
        """
        config = get_integration_config(integration_id)
        if not config:
            raise ValueError(f"Unknown integration: {integration_id}")

        user_id = self._get_user_id()
        state = self._load_state()
        connection = state.get('connections', {}).get(integration_id, {})

        # Remove MCP server if it exists (sync function, don't await)
        mcp_server_id = connection.get('mcp_server_id')
        if mcp_server_id:
            try:
                mcp_service = get_mcp_service()
                mcp_service.delete_server_config(mcp_server_id)
                logger.info(f"[Composio] Removed MCP server: {mcp_server_id}")
            except Exception as e:
                logger.warning(f"[Composio] Failed to remove MCP server: {e}")

            # Remove tokens from secure store
            try:
                token_store = get_oauth_token_store()
                token_store.remove_tokens(mcp_server_id)
                logger.info(f"[Composio] Removed tokens for: {mcp_server_id}")
            except Exception as e:
                logger.warning(f"[Composio] Failed to remove tokens: {e}")

        # Call worker to disconnect from Composio
        try:
            await self._make_worker_request(
                'POST',
                f'/disconnect/{integration_id}/{user_id}'
            )
        except Exception as e:
            logger.warning(f"[Composio] Failed to disconnect from Composio: {e}")

        # Update state
        if 'connections' in state and integration_id in state['connections']:
            del state['connections'][integration_id]
            self._save_state(state)

        # Stop refresh task if no more connected integrations
        if not self._has_connected_integrations():
            self._stop_refresh_task()

        return {'status': 'disconnected'}


# Singleton accessor
def get_composio_service() -> ComposioIntegrationService:
    """Get the singleton instance of the Composio integration service."""
    return ComposioIntegrationService.get_instance()
