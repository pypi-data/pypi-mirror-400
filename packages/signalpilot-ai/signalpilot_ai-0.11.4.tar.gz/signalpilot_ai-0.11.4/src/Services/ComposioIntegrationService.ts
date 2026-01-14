import { URLExt } from '@jupyterlab/coreutils';
import { ServerConnection } from '@jupyterlab/services';

/**
 * Integration status type
 */
export type IntegrationStatus = 'disconnected' | 'connecting' | 'connected';

/**
 * Integration info returned from backend
 */
export interface IIntegration {
  id: string;
  name: string;
  description: string;
  status: IntegrationStatus;
  mcpServerId?: string;
}

/**
 * Service for managing Composio OAuth integrations
 * Handles communication with backend and worker for Notion, Slack, and Google Docs integrations
 */
// OAuth timeout in milliseconds (5 minutes)
const OAUTH_TIMEOUT_MS = 5 * 60 * 1000;

export class ComposioIntegrationService {
  private static instance: ComposioIntegrationService;
  private settings: ServerConnection.ISettings;
  private oauthWindow: Window | null = null;
  private messageHandler: ((event: MessageEvent) => void) | null = null;
  private pollTimer: ReturnType<typeof setInterval> | null = null;
  private timeoutTimer: ReturnType<typeof setTimeout> | null = null;

  private constructor() {
    this.settings = ServerConnection.makeSettings();
  }

  static getInstance(): ComposioIntegrationService {
    if (!ComposioIntegrationService.instance) {
      ComposioIntegrationService.instance = new ComposioIntegrationService();
    }
    return ComposioIntegrationService.instance;
  }

  /**
   * Get all integrations with their status
   */
  async getIntegrations(): Promise<{
    integrations: IIntegration[];
    configured: boolean;
  }> {
    try {
      const url = URLExt.join(
        this.settings.baseUrl,
        'signalpilot-ai/integrations'
      );

      const response = await ServerConnection.makeRequest(
        url,
        {},
        this.settings
      );

      if (!response.ok) {
        throw new Error('Failed to fetch integrations');
      }

      const data = await response.json();
      return {
        integrations: data.integrations || [],
        configured: data.configured || false
      };
    } catch (error) {
      console.error('Error fetching integrations:', error);
      return { integrations: [], configured: false };
    }
  }

  /**
   * Initiate OAuth connection for an integration
   * Opens a popup window for the OAuth flow
   */
  async initiateConnection(
    integrationId: string,
    onComplete: (success: boolean, error?: string) => void
  ): Promise<void> {
    try {
      // Get worker URL and user ID from backend
      const url = URLExt.join(
        this.settings.baseUrl,
        `signalpilot-ai/integrations/${integrationId}/connect`
      );

      const response = await ServerConnection.makeRequest(
        url,
        { method: 'POST' },
        this.settings
      );

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Failed to initiate connection');
      }

      const data = await response.json();
      const workerUrl = data.workerUrl;
      const userId = data.userId;

      if (!workerUrl || !userId) {
        throw new Error('Missing worker URL or user ID');
      }

      // Call worker directly to get redirect URL
      const workerResponse = await fetch(workerUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ userId })
      });

      if (!workerResponse.ok) {
        const errorText = await workerResponse.text();
        throw new Error(`Worker error: ${errorText}`);
      }

      const workerData = await workerResponse.json();
      const redirectUrl = workerData.redirectUrl;

      if (!redirectUrl) {
        throw new Error('No redirect URL received from worker');
      }

      // Set up message handler for OAuth callback
      this.setupMessageHandler(integrationId, onComplete);

      // Open OAuth popup
      const width = 600;
      const height = 700;
      const left = window.screenX + (window.outerWidth - width) / 2;
      const top = window.screenY + (window.outerHeight - height) / 2;

      this.oauthWindow = window.open(
        redirectUrl,
        'composio-oauth',
        `width=${width},height=${height},left=${left},top=${top},popup=yes`
      );

      // Check if popup was blocked
      if (!this.oauthWindow) {
        this.cleanupOAuth();
        throw new Error(
          'Popup was blocked. Please allow popups for this site.'
        );
      }

      // Set up timeout for OAuth flow (5 minutes)
      this.timeoutTimer = setTimeout(() => {
        console.log('[OAuth] Timeout reached, cancelling OAuth flow');
        // Close the window if still open
        if (this.oauthWindow && !this.oauthWindow.closed) {
          this.oauthWindow.close();
        }
        this.cleanupOAuth();
        onComplete(false, 'OAuth timed out. Please try again.');
      }, OAUTH_TIMEOUT_MS);

      // Poll to check if window was closed manually
      this.pollTimer = setInterval(() => {
        if (this.oauthWindow?.closed) {
          this.clearTimers();
          // Window was closed, check status
          this.checkConnectionStatus(integrationId)
            .then(status => {
              if (status.status === 'connected') {
                onComplete(true);
              } else {
                // User closed the window without completing OAuth
                onComplete(false, 'OAuth cancelled');
              }
            })
            .catch(() => {
              // Error checking status, treat as cancelled
              onComplete(false, 'OAuth cancelled');
            })
            .finally(() => {
              this.cleanupOAuth();
            });
        }
      }, 1000);
    } catch (error) {
      console.error('Error initiating connection:', error);
      const message = error instanceof Error ? error.message : 'Unknown error';
      onComplete(false, message);
    }
  }

  /**
   * Set up handler for OAuth postMessage callback
   */
  private setupMessageHandler(
    integrationId: string,
    onComplete: (success: boolean, error?: string) => void
  ): void {
    // Remove any existing handler
    this.cleanupOAuth();

    this.messageHandler = async (event: MessageEvent) => {
      // Validate message
      if (
        !event.data ||
        event.data.type !== 'composio-oauth-complete' ||
        event.data.integration !== integrationId
      ) {
        return;
      }

      // Close the OAuth window
      if (this.oauthWindow && !this.oauthWindow.closed) {
        this.oauthWindow.close();
      }

      this.cleanupOAuth();

      if (event.data.status === 'success') {
        // Complete the connection on the backend
        try {
          await this.completeConnection(integrationId);
          onComplete(true);
        } catch (error) {
          const message =
            error instanceof Error ? error.message : 'Failed to complete setup';
          onComplete(false, message);
        }
      } else {
        onComplete(false, 'OAuth failed');
      }
    };

    window.addEventListener('message', this.messageHandler);
  }

  /**
   * Clear polling and timeout timers
   */
  private clearTimers(): void {
    if (this.pollTimer) {
      clearInterval(this.pollTimer);
      this.pollTimer = null;
    }
    if (this.timeoutTimer) {
      clearTimeout(this.timeoutTimer);
      this.timeoutTimer = null;
    }
  }

  /**
   * Clean up all OAuth state (timers, handlers, window reference)
   */
  private cleanupOAuth(): void {
    this.clearTimers();
    if (this.messageHandler) {
      window.removeEventListener('message', this.messageHandler);
      this.messageHandler = null;
    }
    this.oauthWindow = null;
  }

  /**
   * Complete OAuth connection and create MCP server
   */
  async completeConnection(integrationId: string): Promise<{
    status: IntegrationStatus;
    mcpServerId?: string;
  }> {
    const url = URLExt.join(
      this.settings.baseUrl,
      `signalpilot-ai/integrations/${integrationId}/complete`
    );

    const response = await ServerConnection.makeRequest(
      url,
      { method: 'POST' },
      this.settings
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to complete connection');
    }

    const data = await response.json();
    return {
      status: data.status,
      mcpServerId: data.mcpServerId
    };
  }

  /**
   * Check connection status for an integration
   */
  async checkConnectionStatus(integrationId: string): Promise<{
    status: IntegrationStatus;
    mcpServerId?: string;
  }> {
    const url = URLExt.join(
      this.settings.baseUrl,
      `signalpilot-ai/integrations/${integrationId}/status`
    );

    const response = await ServerConnection.makeRequest(url, {}, this.settings);

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to check status');
    }

    const data = await response.json();
    return {
      status: data.status,
      mcpServerId: data.mcpServerId
    };
  }

  /**
   * Disconnect an integration and remove MCP server
   */
  async disconnect(integrationId: string): Promise<void> {
    const url = URLExt.join(
      this.settings.baseUrl,
      `signalpilot-ai/integrations/${integrationId}`
    );

    const response = await ServerConnection.makeRequest(
      url,
      { method: 'DELETE' },
      this.settings
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to disconnect');
    }
  }
}

// Export singleton instance getter
export const getComposioIntegrationService = () =>
  ComposioIntegrationService.getInstance();
