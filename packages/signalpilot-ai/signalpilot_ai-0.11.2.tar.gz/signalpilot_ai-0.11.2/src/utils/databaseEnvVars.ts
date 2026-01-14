/**
 * Shared utility functions for database environment variable naming
 * Used by NotebookStateService, databaseHelper, and kernelUtils to ensure consistency
 */

import { IDatabaseConfig, DatabaseType } from '../DatabaseStateService';

/**
 * Convert a database name to an environment variable prefix
 * Example: "SignalPilot production DB" -> "SIGNALPILOT_PRODUCTION_DB"
 */
export function getEnvVarPrefix(dbName: string): string {
  return dbName.toUpperCase().replace(/[^A-Z0-9]/g, '_');
}

/**
 * Get the list of environment variable names that would be set for a database config
 * This ensures consistency between what's shown in prompts and what's actually set in the kernel
 */
export function getDatabaseEnvVarNames(config: IDatabaseConfig): string[] {
  const prefix = getEnvVarPrefix(config.name);
  const envVars: string[] = [];

  // Handle credential-based connections
  if (config.connectionType === 'credentials' && config.credentials) {
    // Basic env vars for all credential-based connections
    envVars.push(
      `${prefix}_HOST`,
      `${prefix}_PORT`,
      `${prefix}_DATABASE`,
      `${prefix}_USERNAME`,
      `${prefix}_PASSWORD`,
      `${prefix}_TYPE`,
      `${prefix}_CONNECTION_JSON`
    );

    // Add Snowflake-specific env vars
    if (config.type === DatabaseType.Snowflake) {
      const snowflakeConfig = config.credentials as any;
      envVars.push(`${prefix}_CONNECTION_URL`);
      envVars.push(`${prefix}_ACCOUNT`);
      if (snowflakeConfig.warehouse) {
        envVars.push(`${prefix}_WAREHOUSE`);
      }
      if (snowflakeConfig.role) {
        envVars.push(`${prefix}_ROLE`);
      }
    }

    // Add Databricks-specific env vars
    if (config.type === DatabaseType.Databricks) {
      const databricksConfig = config.credentials as any;
      envVars.push(`${prefix}_CONNECTION_URL`);
      // Note: kernelUtils.ts checks 'authType' in creds (property exists), not if it has a value
      if ('authType' in databricksConfig) {
        envVars.push(`${prefix}_AUTH_TYPE`);
      }
      if (databricksConfig.accessToken) {
        envVars.push(`${prefix}_ACCESS_TOKEN`);
      }
      if (databricksConfig.clientId) {
        envVars.push(`${prefix}_CLIENT_ID`);
      }
      if (databricksConfig.clientSecret) {
        envVars.push(`${prefix}_CLIENT_SECRET`);
      }
      if (databricksConfig.oauthTokenUrl) {
        envVars.push(`${prefix}_OAUTH_TOKEN_URL`);
      }
      if (databricksConfig.warehouseId) {
        envVars.push(`${prefix}_WAREHOUSE_ID`);
      }
      if (databricksConfig.warehouseHttpPath) {
        envVars.push(`${prefix}_WAREHOUSE_HTTP_PATH`);
      }
      if (databricksConfig.catalog) {
        envVars.push(`${prefix}_CATALOG`);
      }
      if (databricksConfig.schema) {
        envVars.push(`${prefix}_SCHEMA`);
      }
    }
  }

  // Handle URL-based connections
  if (config.connectionType === 'url' && config.urlConnection) {
    envVars.push(
      `${prefix}_CONNECTION_URL`,
      `${prefix}_TYPE`,
      `${prefix}_CONNECTION_JSON`
    );
  }

  return envVars;
}

/**
 * Format environment variable names as a string for display in prompts
 * @param config Database configuration
 * @param indent Indentation string (default: 4 spaces)
 */
export function formatEnvVarsForPrompt(
  config: IDatabaseConfig,
  indent: string = '    '
): string {
  const envVars = getDatabaseEnvVarNames(config);
  return envVars.map(v => `${indent}${v}`).join('\n');
}
