import { LabIcon } from '@jupyterlab/ui-components';
import notionIcon from '../../style/icons/integrations/notion.svg';
import slackIcon from '../../style/icons/integrations/slack.svg';
import googleDocsIcon from '../../style/icons/integrations/google-docs.svg';

export const NOTION_ICON = new LabIcon({
  name: 'signalpilot-ai:notion-icon',
  svgstr: notionIcon
});

export const SLACK_ICON = new LabIcon({
  name: 'signalpilot-ai:slack-icon',
  svgstr: slackIcon
});

export const GOOGLE_DOCS_ICON = new LabIcon({
  name: 'signalpilot-ai:google-docs-icon',
  svgstr: googleDocsIcon
});

// Helper function to get integration icon by ID
export const getIntegrationIconComponent = (
  integrationId: string | undefined
): LabIcon | null => {
  switch (integrationId) {
    case 'notion':
      return NOTION_ICON;
    case 'slack':
      return SLACK_ICON;
    case 'google':
      return GOOGLE_DOCS_ICON;
    default:
      return null;
  }
};

// Helper to get display name for integration
export const getIntegrationDisplayName = (
  integrationId: string | undefined
): string => {
  switch (integrationId) {
    case 'notion':
      return 'Notion';
    case 'slack':
      return 'Slack';
    case 'google':
      return 'Google Docs';
    default:
      return integrationId || 'Unknown';
  }
};
