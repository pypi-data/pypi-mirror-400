/**
 * Skills and Tool Search Configuration
 *
 * Configuration for Anthropic Agent Skills and Tool Search features
 */

import { MCPClientService } from './MCPClientService';

/**
 * DBT skill configuration - only enabled when dbt MCP server is available
 */
const DBT_SKILL = {
  type: 'custom' as const,
  skill_id: 'skill_01QQwom54HeQEvdNfksXc4ki',
  version: 'latest'
} as const;

/**
 * Check if dbt MCP server is connected
 */
export async function isDbtServerConnected(): Promise<boolean> {
  try {
    const mcpClient = MCPClientService.getInstance();
    const servers = await mcpClient.getServers();

    // Look for dbt server that is connected and enabled
    const dbtServer = servers.find(
      server =>
        server.id === 'dbt' &&
        server.status === 'connected' &&
        server.enabled !== false
    );

    return !!dbtServer;
  } catch (error) {
    console.error('Error checking dbt server connection:', error);
    return false;
  }
}

/**
 * Get skills to include in API requests based on available MCP servers
 * These include both Anthropic-managed skills and custom skills that extend Claude's capabilities
 */
export async function getAnthropicSkills() {
  const skills = [];

  // Only include dbt skill if dbt MCP server is connected
  if (await isDbtServerConnected()) {
    skills.push(DBT_SKILL);
  }

  return skills;
}

/**
 * Synchronous version for backwards compatibility - returns empty array if async check needed
 */
export const ANTHROPIC_SKILLS = [] as const;

/**
 * Configuration for tool search
 */
export const TOOL_SEARCH_CONFIG = {
  // Enable tool search for MCP tools
  enableToolSearch: true,

  // Tool search variant: 'regex' or 'bm25'
  variant: 'regex' as const,

  // Defer loading for MCP tools by default
  deferMCPTools: true,

  // Beta headers required for skills and tool search
  betaHeaders: [
    'advanced-tool-use-2025-11-20',
    // TODO: Disabled because it's conflicting with the terminal-execute_command tool
    // 'code-execution-2025-08-25',
    'token-efficient-tools-2025-02-19',
    'fine-grained-tool-streaming-2025-05-14'
  ] as string[]
};

/**
 * Get the tool search tool definition
 */
export function getToolSearchTool(variant: 'regex' | 'bm25' = 'bm25') {
  const toolType =
    variant === 'regex'
      ? 'tool_search_tool_regex_20251119'
      : 'tool_search_tool_bm25_20251119';

  const toolName =
    variant === 'regex' ? 'tool_search_tool_regex' : 'tool_search_tool_bm25';

  return {
    type: toolType,
    name: toolName
  };
}

/**
 * Check if skills are enabled (async version)
 */
export async function areSkillsEnabled(): Promise<boolean> {
  const skills = await getAnthropicSkills();
  return skills.length > 0;
}

/**
 * Synchronous version for backwards compatibility
 */
export function areSkillsEnabledSync(): boolean {
  return ANTHROPIC_SKILLS.length > 0;
}

/**
 * Get the container configuration for skills (async version)
 */
export async function getSkillsContainer() {
  if (!(await areSkillsEnabled())) {
    return undefined;
  }

  const skills = await getAnthropicSkills();
  return {
    skills
  };
}

/**
 * Synchronous version for backwards compatibility
 */
export function getSkillsContainerSync() {
  if (!areSkillsEnabledSync()) {
    return undefined;
  }

  return {
    skills: ANTHROPIC_SKILLS
  };
}
