import * as React from 'react';
import {
  IIntegration,
  IntegrationStatus
} from '../../Services/ComposioIntegrationService';
import { getIntegrationIconComponent } from '../integrationIcons';

interface IIntegrationCardProps {
  integration: IIntegration;
  onConnect: (integrationId: string) => void;
  onDisconnect: (integrationId: string) => void;
}

export const IntegrationCard: React.FC<IIntegrationCardProps> = ({
  integration,
  onConnect,
  onDisconnect
}) => {
  const [isConnecting, setIsConnecting] = React.useState(false);

  const handleConnect = () => {
    setIsConnecting(true);
    onConnect(integration.id);
  };

  const handleDisconnect = () => {
    setIsConnecting(true);
    onDisconnect(integration.id);
  };

  // Reset connecting state when status changes
  React.useEffect(() => {
    if (
      integration.status === 'connected' ||
      integration.status === 'disconnected'
    ) {
      setIsConnecting(false);
    }
  }, [integration.status]);

  const getStatusDot = (status: IntegrationStatus) => {
    switch (status) {
      case 'connected':
        return (
          <span
            className="mcp-status-dot mcp-status-dot-connected"
            title="Connected"
          ></span>
        );
      case 'connecting':
        return (
          <span
            className="mcp-status-dot mcp-status-dot-connecting"
            title="Connecting..."
          ></span>
        );
      default:
        return (
          <span
            className="mcp-status-dot mcp-status-dot-disconnected"
            title="Disconnected"
          ></span>
        );
    }
  };

  const status = isConnecting ? 'connecting' : integration.status;
  const IntegrationIcon = getIntegrationIconComponent(integration.id);

  return (
    <div className="mcp-connection-card integration-card">
      <div className="mcp-card-single-line">
        <div className="mcp-card-left">
          {getStatusDot(status)}
          {IntegrationIcon && (
            <IntegrationIcon.react tag="span" className="integration-icon" />
          )}
          <div className="integration-info">
            <span className="mcp-server-name">{integration.name}</span>
            <span className="integration-description">
              {integration.description}
            </span>
          </div>
        </div>
        <div className="mcp-card-right">
          {status === 'connected' ? (
            <button
              className="mcp-button mcp-button-secondary mcp-button-small"
              onClick={handleDisconnect}
              disabled={isConnecting}
            >
              Disconnect
            </button>
          ) : (
            <button
              className="mcp-button mcp-button-primary mcp-button-small"
              onClick={handleConnect}
              disabled={isConnecting}
            >
              {status === 'connecting' ? 'Connecting...' : 'Connect'}
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
