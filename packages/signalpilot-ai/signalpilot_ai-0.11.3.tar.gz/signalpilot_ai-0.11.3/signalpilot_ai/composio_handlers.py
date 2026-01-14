"""
Composio Integration Handlers - Tornado HTTP handlers for OAuth integrations
Provides REST API for managing Composio OAuth integrations (Notion, Slack, Google)
"""
import json
import logging
import traceback
import tornado
from jupyter_server.base.handlers import APIHandler
from .composio_service import get_composio_service

logger = logging.getLogger(__name__)

# Enable debug logging
logger.setLevel(logging.DEBUG)


class IntegrationsHandler(APIHandler):
    """Handler for listing all integrations and their status"""

    @tornado.web.authenticated
    async def get(self):
        """Get all available integrations with their connection status"""
        try:
            service = get_composio_service()
            integrations = service.get_integrations()

            self.finish(json.dumps({
                'integrations': integrations,
                'configured': service.is_configured(),
                'workerUrl': service.get_worker_url() if service.is_configured() else None,
            }))
        except Exception as e:
            logger.error(f"Error getting integrations: {e}")
            logger.error(traceback.format_exc())
            self.set_status(500)
            self.finish(json.dumps({
                'error': str(e)
            }))


class IntegrationConnectHandler(APIHandler):
    """Handler for initiating OAuth connection for an integration"""

    @tornado.web.authenticated
    async def post(self, integration_id):
        """
        Get worker URL and user ID for initiating OAuth connection.
        Frontend will call the worker directly.
        """
        try:
            service = get_composio_service()

            if not service.is_configured():
                self.set_status(400)
                self.finish(json.dumps({
                    'error': 'Composio worker URL not configured. Set COMPOSIO_WORKER_URL environment variable.',
                    'configured': False,
                }))
                return

            result = service.get_initiate_url(integration_id)

            self.finish(json.dumps({
                'success': True,
                'workerUrl': result['workerUrl'],
                'userId': result['userId'],
            }))
        except ValueError as e:
            self.set_status(400)
            self.finish(json.dumps({
                'error': str(e)
            }))
        except Exception as e:
            logger.error(f"Error initiating connection for {integration_id}: {e}")
            logger.error(traceback.format_exc())
            self.set_status(500)
            self.finish(json.dumps({
                'error': str(e)
            }))


class IntegrationCompleteHandler(APIHandler):
    """Handler for completing OAuth connection after callback"""

    @tornado.web.authenticated
    async def post(self, integration_id):
        """Complete OAuth connection and create MCP server"""
        try:
            service = get_composio_service()

            if not service.is_configured():
                self.set_status(400)
                self.finish(json.dumps({
                    'error': 'Composio worker URL not configured',
                    'configured': False,
                }))
                return

            result = await service.complete_connection(integration_id)

            self.finish(json.dumps({
                'success': True,
                **result,
            }))
        except ValueError as e:
            self.set_status(400)
            self.finish(json.dumps({
                'error': str(e)
            }))
        except Exception as e:
            logger.error(f"Error completing connection for {integration_id}: {e}")
            logger.error(traceback.format_exc())
            self.set_status(500)
            self.finish(json.dumps({
                'error': str(e)
            }))


class IntegrationStatusHandler(APIHandler):
    """Handler for checking connection status of an integration"""

    @tornado.web.authenticated
    async def get(self, integration_id):
        """Check connection status for an integration"""
        try:
            service = get_composio_service()

            if not service.is_configured():
                self.set_status(400)
                self.finish(json.dumps({
                    'error': 'Composio worker URL not configured',
                    'configured': False,
                }))
                return

            result = await service.check_connection_status(integration_id)

            self.finish(json.dumps({
                'success': True,
                **result,
            }))
        except ValueError as e:
            self.set_status(400)
            self.finish(json.dumps({
                'error': str(e)
            }))
        except Exception as e:
            logger.error(f"Error checking status for {integration_id}: {e}")
            logger.error(traceback.format_exc())
            self.set_status(500)
            self.finish(json.dumps({
                'error': str(e)
            }))


class IntegrationDisconnectHandler(APIHandler):
    """Handler for disconnecting an integration"""

    @tornado.web.authenticated
    async def delete(self, integration_id):
        """Disconnect an integration and remove MCP server"""
        try:
            service = get_composio_service()

            result = await service.disconnect(integration_id)

            self.finish(json.dumps({
                'success': True,
                **result,
            }))
        except ValueError as e:
            self.set_status(400)
            self.finish(json.dumps({
                'error': str(e)
            }))
        except Exception as e:
            logger.error(f"Error disconnecting {integration_id}: {e}")
            logger.error(traceback.format_exc())
            self.set_status(500)
            self.finish(json.dumps({
                'error': str(e)
            }))


class IntegrationRefreshHandler(APIHandler):
    """Handler for manually refreshing OAuth tokens for an integration"""

    @tornado.web.authenticated
    async def post(self, integration_id):
        """
        Manually trigger token refresh for an integration.
        Fetches fresh credentials from Composio and updates MCP server if tokens changed.
        """
        try:
            service = get_composio_service()

            if not service.is_configured():
                self.set_status(400)
                self.finish(json.dumps({
                    'error': 'Composio worker URL not configured',
                    'configured': False,
                }))
                return

            result = await service.refresh_token(integration_id)

            self.finish(json.dumps({
                'success': result.get('success', False),
                'tokens_updated': result.get('tokens_updated', False),
                'error': result.get('error'),
            }))
        except ValueError as e:
            self.set_status(400)
            self.finish(json.dumps({
                'error': str(e)
            }))
        except Exception as e:
            logger.error(f"Error refreshing tokens for {integration_id}: {e}")
            logger.error(traceback.format_exc())
            self.set_status(500)
            self.finish(json.dumps({
                'error': str(e)
            }))
