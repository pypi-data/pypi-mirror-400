"""
Integration Configuration for Composio OAuth Apps
This file contains static configuration for integrations with MCP servers.
IMPORTANT: This file is NOT exposed to the frontend for security reasons.
"""

import base64
import json
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

# Integration configuration - defines how to set up MCP servers after OAuth
INTEGRATION_CONFIG: Dict[str, Dict[str, Any]] = {
    'notion': {
        'id': 'notion',
        'name': 'Notion',
        'description': 'Connect to Notion workspaces for reading and searching pages',
        'mcp_server_id': 'notion-integration',
        'mcp_server_name': 'Notion (Composio)',
        'mcp_command': 'npx',
        'mcp_args': ['-y', '@notionhq/notion-mcp-server'],
        # Maps Composio credential fields to MCP server env vars
        'env_mapping': {
            'access_token': 'NOTION_TOKEN',
        },
        'whitelisted_tools': [
            'API-post-search',
            'API-get-block-children',
            'API-retrieve-a-page',
            'API-retrieve-a-database',
            'API-post-database-query',
        ],
    },
    'slack': {
        'id': 'slack',
        'name': 'Slack',
        'description': 'Connect to Slack workspaces for searching and reading messages',
        'mcp_server_id': 'slack-integration',
        'mcp_server_name': 'Slack (Composio)',
        # Note: This requires the slack-mcp-server to be installed
        # Using npx with a placeholder - user may need to adjust based on their setup
        'mcp_command': 'npx',
        'mcp_args': ['-y', 'slack-mcp-server@latest', '--transport', 'stdio'],
        # Maps Composio credential fields to MCP server env vars
        'env_mapping': {
            'access_token': 'SLACK_MCP_XOXP_TOKEN',
        },
        'whitelisted_tools': [
            'conversations_search_messages',
            'conversations_history',
            'conversations_replies',
            'channels_list',
        ],
    },
    'google': {
        'id': 'google',
        'name': 'Google Docs',
        'description': 'Connect to Google Drive and Docs for searching and reading documents',
        'mcp_server_id': 'google-integration',
        'mcp_server_name': 'Google Docs (Composio)',
        # Note: This requires uvx to be installed
        # --single-user makes USER_GOOGLE_EMAIL the default, skipping email in tool calls
        'mcp_command': 'uvx',
        'mcp_args': ['workspace-mcp', '--tools', 'drive', 'docs', '--single-user'],
        # Maps Composio credential fields to MCP server env vars
        'env_mapping': {
            'client_id': 'GOOGLE_OAUTH_CLIENT_ID',
            'client_secret': 'GOOGLE_OAUTH_CLIENT_SECRET',
            'access_token': 'GOOGLE_ACCESS_TOKEN',
            'refresh_token': 'GOOGLE_REFRESH_TOKEN',
            'email': 'USER_GOOGLE_EMAIL',  # User's Google email from OAuth
        },
        'whitelisted_tools': [
            'start_google_auth',
            'search_docs',
            'get_doc_content',
            'list_docs_in_folder',
            'inspect_doc_structure',
            'read_document_comments',
            'create_document_comment',
            'reply_to_document_comment',
            'resolve_document_comment',
            'search_drive_files',
            'list_drive_items',
            'get_drive_file_content',
            'get_drive_file_download_url',
            'list_drive_items_in_folder',
        ],
    },
}


def get_integration_config(integration_id: str) -> Dict[str, Any] | None:
    """Get configuration for a specific integration."""
    return INTEGRATION_CONFIG.get(integration_id)


def get_all_integration_ids() -> List[str]:
    """Get list of all integration IDs."""
    return list(INTEGRATION_CONFIG.keys())


def get_integration_info_for_frontend() -> List[Dict[str, str]]:
    """
    Get integration info safe to expose to frontend.
    Only includes id, name, and description - no MCP commands or env mappings.
    """
    return [
        {
            'id': config['id'],
            'name': config['name'],
            'description': config['description'],
        }
        for config in INTEGRATION_CONFIG.values()
    ]


def get_mcp_server_config(integration_id: str, credentials: Dict[str, Any]) -> Dict[str, Any] | None:
    """
    Generate MCP server configuration for an integration.
    Maps credentials from Composio to the appropriate env vars for the MCP server.

    DEPRECATED: Use get_mcp_server_config_for_storage() and store tokens separately.
    """
    config = INTEGRATION_CONFIG.get(integration_id)
    if not config:
        return None

    # Build environment variables from credentials
    env = {}
    for cred_field, env_var in config['env_mapping'].items():
        if cred_field in credentials:
            env[env_var] = credentials[cred_field]

    return {
        'id': config['mcp_server_id'],
        'name': config['mcp_server_name'],
        'command': config['mcp_command'],
        'args': config['mcp_args'],
        'env': env,
        'enabled': True,
        'enabledTools': config['whitelisted_tools'],
    }


def get_mcp_server_config_for_storage(integration_id: str) -> Dict[str, Any] | None:
    """
    Generate MCP server configuration for storage (WITHOUT credentials).
    Tokens should be stored separately using OAuthTokenStore and injected at runtime.

    Returns config suitable for mcp.json without sensitive data.
    """
    config = INTEGRATION_CONFIG.get(integration_id)
    if not config:
        return None

    return {
        'id': config['mcp_server_id'],
        'name': config['mcp_server_name'],
        'command': config['mcp_command'],
        'args': config['mcp_args'],
        # No env vars with tokens - they're stored securely elsewhere
        'enabled': True,
        'enabledTools': config['whitelisted_tools'],
        # Mark as OAuth integration so MCP service knows to look up tokens
        'isOAuthIntegration': True,
    }


def _extract_email_from_id_token(id_token: str) -> str | None:
    """
    Extract email from a Google OAuth id_token (JWT).

    The id_token is a JWT with three parts: header.payload.signature
    We decode the payload to get the email claim.
    """
    try:
        # JWT has 3 parts separated by dots
        parts = id_token.split('.')
        if len(parts) != 3:
            return None

        # Decode the payload (second part)
        # Add padding if needed for base64 decoding
        payload_b64 = parts[1]
        padding = 4 - len(payload_b64) % 4
        if padding != 4:
            payload_b64 += '=' * padding

        payload_json = base64.urlsafe_b64decode(payload_b64)
        payload = json.loads(payload_json)

        # Extract email from claims
        email = payload.get('email')
        if email:
            logger.debug(f"[Integrations] Extracted email from id_token: {email}")
            return email

        return None
    except Exception as e:
        logger.warning(f"[Integrations] Failed to extract email from id_token: {e}")
        return None


def build_env_from_credentials(integration_id: str, credentials: Dict[str, Any]) -> Dict[str, str]:
    """
    Build environment variables from Composio credentials.

    Args:
        integration_id: The integration ID
        credentials: Credentials from Composio

    Returns:
        Dict of environment variable name -> value
    """
    config = INTEGRATION_CONFIG.get(integration_id)
    if not config:
        return {}

    env = {}
    for cred_field, env_var in config['env_mapping'].items():
        if cred_field in credentials:
            env[env_var] = credentials[cred_field]

    # For Google integration, try to extract email from various sources if not directly available
    if integration_id == 'google' and 'USER_GOOGLE_EMAIL' not in env:
        email = None

        # Try common field names for email
        for field_name in ['email', 'userEmail', 'user_email', 'Email']:
            if field_name in credentials:
                email = credentials[field_name]
                break

        # Try to extract from id_token if not found directly
        if not email:
            id_token = credentials.get('id_token')
            if id_token:
                email = _extract_email_from_id_token(id_token)

        if email:
            env['USER_GOOGLE_EMAIL'] = email
        else:
            logger.warning(f"[Integrations] Could not find email in Google credentials. Keys: {list(credentials.keys())}")

    return env


def get_mcp_server_id_for_integration(integration_id: str) -> str | None:
    """Get the MCP server ID for an integration."""
    config = INTEGRATION_CONFIG.get(integration_id)
    if config:
        return config['mcp_server_id']
    return None
