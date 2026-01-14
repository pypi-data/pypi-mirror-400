import { BehaviorSubject, Observable, Subject } from 'rxjs';
import { v4 as uuidv4 } from 'uuid';
import { DatabaseEncoder } from './utils/databaseEncoder';
import {
  DatabaseTools,
  DatabaseType as DBToolsType
} from './BackendTools/DatabaseTools';
import { StateDBCachingService } from './utils/backendCaching';

/**
 * Supported database types
 */
export enum DatabaseType {
  MySQL = 'mysql',
  PostgreSQL = 'postgresql',
  Snowflake = 'snowflake',
  Databricks = 'databricks'
}

/**
 * Base database credentials interface
 */
export interface IDatabaseCredentials {
  id: string;
  name: string;
  description: string;
  type: DatabaseType;
  host: string;
  port: number;
  database: string;
  username: string;
  password: string;
  // Created/updated timestamps
  createdAt: string;
  updatedAt: string;
}

/**
 * MySQL specific database credentials
 */
export interface IMySQLCredentials extends IDatabaseCredentials {
  type: DatabaseType.MySQL;
}

/**
 * PostgreSQL specific database credentials
 */
export interface IPostgreSQLCredentials extends IDatabaseCredentials {
  type: DatabaseType.PostgreSQL;
}

/**
 * Snowflake specific database credentials
 */
export interface ISnowflakeCredentials extends IDatabaseCredentials {
  type: DatabaseType.Snowflake;
  connectionUrl: string;
  warehouse?: string;
  role?: string;
}

/**
 * Databricks authentication type
 */
export type DatabricksAuthType = 'pat' | 'service_principal';

/**
 * Databricks specific database credentials
 */
export interface IDatabricksCredentials extends IDatabaseCredentials {
  type: DatabaseType.Databricks;
  connectionUrl: string; // Databricks Host (e.g., https://dbc-xxxxxx-xxxx.cloud.databricks.com)
  authType: DatabricksAuthType;
  // PAT authentication
  accessToken?: string;
  // Service Principal authentication
  clientId?: string;
  clientSecret?: string;
  oauthTokenUrl?: string;
  // Optional fields
  warehouseId?: string;
  warehouseHttpPath?: string;
  catalog: string;
  schema?: string;
}

/**
 * Database schema type definitions
 */

// MySQL/PostgreSQL schema types
export interface IDatabaseColumn {
  column_name: string;
  data_type: string;
  is_nullable: string;
  column_default: string | null;
  character_maximum_length: number | null;
  numeric_precision: number | null;
  numeric_scale: number | null;
}

export interface IForeignKey {
  column_name: string;
  foreign_table_schema: string;
  foreign_table_name: string;
  foreign_column_name: string;
}

export interface IIndex {
  indexname: string;
  indexdef: string;
}

export interface ITableSchema {
  schema: string;
  table_name: string;
  full_name: string;
  columns: IDatabaseColumn[];
  primary_keys: string[];
  foreign_keys: IForeignKey[];
  indices: IIndex[];
}

// Schema wrapper for MySQL/PostgreSQL databases
export interface IMySQLPostgreSQLSchema {
  table_schemas: {
    [tableName: string]: ITableSchema;
  };
}

// Snowflake schema types
export interface IColumnBase {
  name: string;
  type: string;
  ordinal: number;
  nullable: boolean;
  [extra: string]: unknown;
}

export interface INumberColumn extends IColumnBase {
  type: 'NUMBER';
  precision: number;
  scale: number;
}

export interface ITextColumn extends IColumnBase {
  type: 'TEXT';
  max_length: number;
  description?: string;
}

export interface IDateColumn extends IColumnBase {
  type: 'DATE';
}

export type Column =
  | INumberColumn
  | ITextColumn
  | IDateColumn
  | (IColumnBase & {
      type: Exclude<string, 'NUMBER' | 'TEXT' | 'DATE'>;
    });

export interface ITableEntry {
  schema: string;
  table: string;
  type: string;
  columns: Column[];
}

export interface ISchemaEntry {
  schema: string;
  tables: ITableEntry[];
  error: string | null;
}

export interface IDatabaseDefinition {
  database: string;
  schemas: ISchemaEntry[];
}

export interface ISnowflakeSchemaData {
  databases: IDatabaseDefinition[];
}

/**
 * Database URL connection for URL-based connections
 */
export interface IDatabaseUrlConnection {
  id: string;
  name: string;
  description: string;
  type: DatabaseType;
  connectionUrl: string;
  // Created/updated timestamps
  createdAt: string;
  updatedAt: string;
}

/**
 * Database configuration (either credentials or URL-based)
 */
export interface IDatabaseConfig {
  id: string;
  name: string;
  type: DatabaseType;
  connectionType: 'credentials' | 'url';
  // Connection details (one will be null based on connectionType)
  credentials?:
    | IMySQLCredentials
    | IPostgreSQLCredentials
    | ISnowflakeCredentials
    | IDatabricksCredentials;
  urlConnection?: IDatabaseUrlConnection;
  // Schema information
  schema_last_updated?: string | null;
  database_schema?: IMySQLPostgreSQLSchema | ISnowflakeSchemaData | null;
  // Metadata
  createdAt: string;
  updatedAt: string;
}

/**
 * Database credentials state interface
 */
interface IDatabaseCredentialsState {
  // Credential management
  configurations: IDatabaseConfig[];
  activeConfigId: string | null;
  activeConfig: IDatabaseConfig | null;

  // Service state
  isInitialized: boolean;
}

/**
 * Initial database credentials state
 */
const initialDatabaseCredentialsState: IDatabaseCredentialsState = {
  // Configuration management
  configurations: [],
  activeConfigId: null,
  activeConfig: null,

  // Service state
  isInitialized: false
};

// State observable
const databaseCredentialsState$ =
  new BehaviorSubject<IDatabaseCredentialsState>(
    initialDatabaseCredentialsState
  );

// Event subjects for configuration changes
const configAdded$ = new Subject<IDatabaseConfig>();
const configRemoved$ = new Subject<{
  configId: string;
  config: IDatabaseConfig;
}>();
const configUpdated$ = new Subject<IDatabaseConfig>();
const activeConfigChanged$ = new Subject<{
  oldConfigId: string | null;
  newConfigId: string | null;
}>();

/**
 * Database Credentials State Service
 * Manages database credential configurations using RxJS
 */
export const DatabaseStateService = {
  /**
   * Get the current database credentials state
   */
  getState: () => databaseCredentialsState$.getValue(),

  /**
   * Update the database credentials state with partial values
   */
  setState: (partial: Partial<IDatabaseCredentialsState>) =>
    databaseCredentialsState$.next({
      ...databaseCredentialsState$.getValue(),
      ...partial
    }),

  /**
   * Subscribe to state changes
   */
  changes: databaseCredentialsState$.asObservable(),

  /**
   * Initialize the database credentials service
   */
  initialize: () => {
    DatabaseStateService.setState({ isInitialized: true });
  },

  /**
   * Create a new MySQL database configuration using credentials
   */
  createMySQLConfig: (
    name: string,
    description: string,
    host: string,
    port: number,
    database: string,
    username: string,
    password: string
  ): IDatabaseConfig => {
    const id = uuidv4();
    const now = new Date().toISOString();

    const credentials: IMySQLCredentials = {
      id,
      name,
      description,
      type: DatabaseType.MySQL,
      host,
      port,
      database,
      username,
      password,
      createdAt: now,
      updatedAt: now
    };

    const config: IDatabaseConfig = {
      id,
      name,
      type: DatabaseType.MySQL,
      connectionType: 'credentials',
      credentials,
      urlConnection: undefined,
      schema_last_updated: null,
      database_schema: null,
      createdAt: now,
      updatedAt: now
    };

    // Add to configurations array
    const currentState = DatabaseStateService.getState();
    const updatedConfigurations = [...currentState.configurations, config];
    DatabaseStateService.setState({ configurations: updatedConfigurations });

    // Emit config added event
    configAdded$.next(config);

    return config;
  },

  /**
   * Create a new PostgreSQL database configuration using credentials
   */
  createPostgreSQLConfig: (
    name: string,
    description: string,
    host: string,
    port: number,
    database: string,
    username: string,
    password: string
  ): IDatabaseConfig => {
    const id = uuidv4();
    const now = new Date().toISOString();

    const credentials: IPostgreSQLCredentials = {
      id,
      name,
      description,
      type: DatabaseType.PostgreSQL,
      host,
      port,
      database,
      username,
      password,
      createdAt: now,
      updatedAt: now
    };

    const config: IDatabaseConfig = {
      id,
      name,
      type: DatabaseType.PostgreSQL,
      connectionType: 'credentials',
      credentials,
      urlConnection: undefined,
      schema_last_updated: null,
      database_schema: null,
      createdAt: now,
      updatedAt: now
    };

    // Add to configurations array
    const currentState = DatabaseStateService.getState();
    const updatedConfigurations = [...currentState.configurations, config];
    DatabaseStateService.setState({ configurations: updatedConfigurations });

    // Emit config added event
    configAdded$.next(config);

    return config;
  },

  /**
   * Create a new Snowflake database configuration using credentials
   */
  createSnowflakeConfig: (
    name: string,
    description: string,
    connectionUrl: string,
    username: string,
    password: string,
    database?: string,
    warehouse?: string,
    role?: string
  ): IDatabaseConfig => {
    const id = uuidv4();
    const now = new Date().toISOString();

    const credentials: ISnowflakeCredentials = {
      id,
      name,
      description,
      type: DatabaseType.Snowflake,
      host: '', // Not used for Snowflake
      port: 443,
      database: database || '',
      username,
      password,
      connectionUrl,
      warehouse,
      role,
      createdAt: now,
      updatedAt: now
    };

    const config: IDatabaseConfig = {
      id,
      name,
      type: DatabaseType.Snowflake,
      connectionType: 'credentials',
      credentials,
      urlConnection: undefined,
      schema_last_updated: null,
      database_schema: null,
      createdAt: now,
      updatedAt: now
    };

    // Add to configurations array
    const currentState = DatabaseStateService.getState();
    const updatedConfigurations = [...currentState.configurations, config];
    DatabaseStateService.setState({ configurations: updatedConfigurations });

    // Emit config added event
    configAdded$.next(config);

    return config;
  },

  /**
   * Create a new Databricks database configuration using credentials
   */
  createDatabricksConfig: (
    name: string,
    description: string,
    connectionUrl: string,
    authType: DatabricksAuthType,
    catalog: string,
    accessToken?: string,
    clientId?: string,
    clientSecret?: string,
    warehouseHttpPath?: string,
    dbSchema?: string
  ): IDatabaseConfig => {
    const id = uuidv4();
    const now = new Date().toISOString();

    const credentials: IDatabricksCredentials = {
      id,
      name,
      description,
      type: DatabaseType.Databricks,
      host: '', // Not used for Databricks
      port: 443,
      database: catalog || '',
      username: authType === 'pat' ? 'token' : clientId || '',
      password: authType === 'pat' ? accessToken || '' : clientSecret || '',
      connectionUrl,
      authType,
      accessToken: authType === 'pat' ? accessToken : undefined,
      clientId: authType === 'service_principal' ? clientId : undefined,
      clientSecret: authType === 'service_principal' ? clientSecret : undefined,
      warehouseHttpPath,
      catalog,
      schema: dbSchema,
      createdAt: now,
      updatedAt: now
    };

    const config: IDatabaseConfig = {
      id,
      name,
      type: DatabaseType.Databricks,
      connectionType: 'credentials',
      credentials,
      urlConnection: undefined,
      schema_last_updated: null,
      database_schema: null,
      createdAt: now,
      updatedAt: now
    };

    // Add to configurations array
    const currentState = DatabaseStateService.getState();
    const updatedConfigurations = [...currentState.configurations, config];
    DatabaseStateService.setState({ configurations: updatedConfigurations });

    // Emit config added event
    configAdded$.next(config);

    return config;
  },

  /**
   * Create a new database configuration using URL
   */
  createUrlConfig: (
    name: string,
    description: string,
    type: DatabaseType,
    connectionUrl: string
  ): IDatabaseConfig => {
    const id = uuidv4();
    const now = new Date().toISOString();

    const urlConnection: IDatabaseUrlConnection = {
      id,
      name,
      description,
      type,
      connectionUrl,
      createdAt: now,
      updatedAt: now
    };

    const config: IDatabaseConfig = {
      id,
      name,
      type,
      connectionType: 'url',
      credentials: undefined,
      urlConnection,
      schema_last_updated: null,
      database_schema: null,
      createdAt: now,
      updatedAt: now
    };

    // Add to configurations array
    const currentState = DatabaseStateService.getState();
    const updatedConfigurations = [...currentState.configurations, config];
    DatabaseStateService.setState({ configurations: updatedConfigurations });

    // Emit config added event
    configAdded$.next(config);

    return config;
  },

  /**
   * Get all database configurations
   */
  getConfigurations: (): IDatabaseConfig[] => {
    return DatabaseStateService.getState().configurations;
  },

  /**
   * Get a specific database configuration by ID
   */
  getConfiguration: (configId: string): IDatabaseConfig | null => {
    const configurations = DatabaseStateService.getState().configurations;
    return configurations.find(config => config.id === configId) || null;
  },

  /**
   * Update an existing database configuration
   */
  updateConfiguration: (
    configId: string,
    updates: Partial<IDatabaseConfig>
  ): boolean => {
    const currentState = DatabaseStateService.getState();
    const configIndex = currentState.configurations.findIndex(
      config => config.id === configId
    );

    if (configIndex === -1) {
      return false;
    }

    const updatedConfig = {
      ...currentState.configurations[configIndex],
      ...updates,
      updatedAt: new Date().toISOString()
    };

    const updatedConfigurations = [...currentState.configurations];
    updatedConfigurations[configIndex] = updatedConfig;

    DatabaseStateService.setState({ configurations: updatedConfigurations });

    // Update active config if it's the same
    if (currentState.activeConfigId === configId) {
      DatabaseStateService.setState({ activeConfig: updatedConfig });
    }

    // Emit config updated event
    configUpdated$.next(updatedConfig);

    return true;
  },

  /**
   * Remove a database configuration
   */
  removeConfiguration: (configId: string): boolean => {
    const currentState = DatabaseStateService.getState();
    const configIndex = currentState.configurations.findIndex(
      config => config.id === configId
    );

    if (configIndex === -1) {
      return false;
    }

    const configToRemove = currentState.configurations[configIndex];
    const updatedConfigurations = currentState.configurations.filter(
      config => config.id !== configId
    );

    DatabaseStateService.setState({ configurations: updatedConfigurations });

    // Clear active config if it was the removed one
    if (currentState.activeConfigId === configId) {
      DatabaseStateService.setState({
        activeConfigId: null,
        activeConfig: null
      });
    }

    // Emit config removed event
    configRemoved$.next({ configId, config: configToRemove });

    return true;
  },

  /**
   * Set the active database configuration
   */
  setActiveConfiguration: (configId: string | null): boolean => {
    const currentState = DatabaseStateService.getState();
    const oldConfigId = currentState.activeConfigId;

    if (configId === null) {
      DatabaseStateService.setState({
        activeConfigId: null,
        activeConfig: null
      });
      activeConfigChanged$.next({ oldConfigId, newConfigId: null });
      return true;
    }

    const config = DatabaseStateService.getConfiguration(configId);
    if (!config) {
      return false;
    }

    DatabaseStateService.setState({
      activeConfigId: configId,
      activeConfig: config
    });

    // Emit active config changed event
    activeConfigChanged$.next({ oldConfigId, newConfigId: configId });

    return true;
  },

  /**
   * Get the currently active configuration
   */
  getActiveConfiguration: (): IDatabaseConfig | null => {
    return DatabaseStateService.getState().activeConfig;
  },

  /**
   * Get configurations by database type
   */
  getConfigurationsByType: (type: DatabaseType): IDatabaseConfig[] => {
    return DatabaseStateService.getState().configurations.filter(
      config => config.type === type
    );
  },

  /**
   * Get configurations by connection type (credentials vs URL)
   */
  getConfigurationsByConnectionType: (
    connectionType: 'credentials' | 'url'
  ): IDatabaseConfig[] => {
    return DatabaseStateService.getState().configurations.filter(
      config => config.connectionType === connectionType
    );
  },

  // Event observables
  /**
   * Subscribe to configuration added events
   */
  onConfigurationAdded: (): Observable<IDatabaseConfig> => {
    return configAdded$.asObservable();
  },

  /**
   * Subscribe to configuration removed events
   */
  onConfigurationRemoved: (): Observable<{
    configId: string;
    config: IDatabaseConfig;
  }> => {
    return configRemoved$.asObservable();
  },

  /**
   * Subscribe to configuration updated events
   */
  onConfigurationUpdated: (): Observable<IDatabaseConfig> => {
    return configUpdated$.asObservable();
  },

  /**
   * Subscribe to active configuration change events
   */
  onActiveConfigurationChanged: (): Observable<{
    oldConfigId: string | null;
    newConfigId: string | null;
  }> => {
    return activeConfigChanged$.asObservable();
  },

  // Schema management methods

  /**
   * Fetch and update schema information for a database configuration
   * @param configId Database configuration ID
   * @returns Promise with schema fetch result
   */
  fetchAndUpdateSchema: async (
    configId: string
  ): Promise<{ success: boolean; error?: string; schema?: string }> => {
    try {
      const config = DatabaseStateService.getConfiguration(configId);
      if (!config) {
        return { success: false, error: 'Database configuration not found' };
      }

      // Build database URL from configuration
      let databaseUrl: string | undefined;
      let dbType: DBToolsType;
      let snowflakeConfig: any;
      let databricksConfig: any;

      if (config.connectionType === 'url' && config.urlConnection) {
        databaseUrl = config.urlConnection.connectionUrl;
        dbType = config.type as unknown as DBToolsType;
      } else if (
        config.connectionType === 'credentials' &&
        config.credentials
      ) {
        const creds = config.credentials;
        dbType = config.type as unknown as DBToolsType;
        // Build connection URL based on database type
        switch (config.type) {
          case DatabaseType.PostgreSQL:
            databaseUrl = `postgresql://${creds.username}:${creds.password}@${creds.host}:${creds.port}/${creds.database}`;
            break;
          case DatabaseType.MySQL:
            databaseUrl = `mysql://${creds.username}:${creds.password}@${creds.host}:${creds.port}/${creds.database}`;
            break;
          case DatabaseType.Snowflake:
            // eslint-disable-next-line no-case-declarations
            const sfCreds = creds as ISnowflakeCredentials;
            // For Snowflake, build a config object with connectionUrl
            snowflakeConfig = {
              type: 'snowflake',
              connectionUrl: sfCreds.connectionUrl,
              username: sfCreds.username,
              password: sfCreds.password,
              warehouse: sfCreds.warehouse || undefined,
              database: sfCreds.database || undefined,
              role: sfCreds.role || undefined
            };
            break;
          case DatabaseType.Databricks:
            // eslint-disable-next-line no-case-declarations
            const dbCreds = creds as IDatabricksCredentials;
            // For Databricks, build a config object
            databricksConfig = {
              type: 'databricks',
              connectionUrl: dbCreds.connectionUrl,
              authType: dbCreds.authType,
              accessToken: dbCreds.accessToken,
              clientId: dbCreds.clientId,
              clientSecret: dbCreds.clientSecret,
              warehouseHttpPath: dbCreds.warehouseHttpPath,
              catalog: dbCreds.catalog || undefined,
              schema: dbCreds.schema || undefined
            };
            break;
          default:
            return {
              success: false,
              error: 'Unsupported database type for schema fetching'
            };
        }
      } else {
        return { success: false, error: 'Invalid database configuration' };
      }

      // Create DatabaseTools instance and fetch schema
      const databaseTools = new DatabaseTools();
      let schemaResult: string;

      if (dbType === DBToolsType.Snowflake && snowflakeConfig) {
        // For Snowflake, use the new API with config object
        schemaResult = await databaseTools.getDatabaseMetadata(
          undefined,
          DBToolsType.Snowflake,
          snowflakeConfig
        );
      } else if (dbType === DBToolsType.Databricks && databricksConfig) {
        // For Databricks, use the config object
        schemaResult = await databaseTools.getDatabaseMetadata(
          undefined,
          DBToolsType.Databricks,
          databricksConfig
        );
      } else {
        // For PostgreSQL/MySQL, use the URL
        schemaResult = await databaseTools.getDatabaseMetadata(
          databaseUrl,
          dbType
        );
      }

      // Parse the result
      let parsedResult;
      try {
        parsedResult = JSON.parse(schemaResult);
      } catch (parseError) {
        return {
          success: false,
          error: `Failed to parse schema result: ${parseError}`
        };
      }

      if (parsedResult.error) {
        return { success: false, error: parsedResult.error };
      }

      // Store the parsed schema object directly
      const schemaToStore = parsedResult.schema_info
        ? typeof parsedResult.schema_info === 'string'
          ? JSON.parse(parsedResult.schema_info)
          : parsedResult.schema_info
        : parsedResult;

      // Update the configuration with schema information
      const now = new Date().toISOString();
      const updateResult = DatabaseStateService.updateConfiguration(configId, {
        schema_last_updated: now,
        database_schema: schemaToStore
      });

      if (!updateResult) {
        return {
          success: false,
          error: 'Failed to update configuration with schema information'
        };
      }

      // Save to StateDB
      await DatabaseStateService.saveConfigurationsToStateDB();

      return {
        success: true,
        schema: schemaToStore
      };
    } catch (error) {
      console.error('[DatabaseStateService] Error fetching schema:', error);
      return {
        success: false,
        error: `Schema fetch failed: ${error instanceof Error ? error.message : String(error)}`
      };
    }
  },

  /**
   * Get schema information for a database configuration
   * @param configId Database configuration ID
   * @returns Schema information or null if not available
   */
  getSchemaInfo: (
    configId: string
  ): { lastUpdated: string | null; schema: any | null } | null => {
    const config = DatabaseStateService.getConfiguration(configId);
    if (!config) {
      return null;
    }

    return {
      lastUpdated: config.schema_last_updated || null,
      schema: config.database_schema || null
    };
  },

  /**
   * Check if schema information is available and fresh for a configuration
   * @param configId Database configuration ID
   * @param maxAgeHours Maximum age in hours before schema is considered stale (default: 24)
   * @returns True if schema is available and fresh
   */
  isSchemaFresh: (configId: string, maxAgeHours: number = 24): boolean => {
    const schemaInfo = DatabaseStateService.getSchemaInfo(configId);
    if (!schemaInfo || !schemaInfo.lastUpdated || !schemaInfo.schema) {
      return false;
    }

    const lastUpdated = new Date(schemaInfo.lastUpdated);
    const now = new Date();
    const ageHours = (now.getTime() - lastUpdated.getTime()) / (1000 * 60 * 60);

    return ageHours <= maxAgeHours;
  },

  // StateDB persistence methods with encoding

  /**
   * Convert internal IDatabaseConfig to TOML format for db.toml storage
   */
  convertConfigToTomlFormat: (config: IDatabaseConfig): any => {
    const tomlConfig: any = {
      name: config.name,
      id: config.id
    };

    if (config.credentials) {
      const creds = config.credentials;
      if (creds.host) tomlConfig.host = creds.host;
      if (creds.port) tomlConfig.port = creds.port;
      if (creds.database) tomlConfig.database = creds.database;
      if (creds.username) tomlConfig.username = creds.username;
      if (creds.password) tomlConfig.password = creds.password;
      if (creds.description) tomlConfig.description = creds.description;

      // Type-specific fields
      if ('connectionUrl' in creds) {
        tomlConfig.account = (creds as ISnowflakeCredentials).connectionUrl;
      }
      if ('warehouse' in creds) {
        tomlConfig.warehouse = (creds as ISnowflakeCredentials).warehouse;
      }
      if ('role' in creds) {
        tomlConfig.role = (creds as ISnowflakeCredentials).role;
      }
      if ('catalog' in creds) {
        tomlConfig.catalog = (creds as IDatabricksCredentials).catalog;
      }
      if ('authType' in creds) {
        tomlConfig.auth_type = (creds as IDatabricksCredentials).authType;
      }
      if ('accessToken' in creds) {
        tomlConfig.access_token = (creds as IDatabricksCredentials).accessToken;
      }
      if ('warehouseHttpPath' in creds) {
        tomlConfig.http_path = (creds as IDatabricksCredentials).warehouseHttpPath;
      }
    }

    if (config.urlConnection) {
      tomlConfig.connection_url = config.urlConnection.connectionUrl;
      tomlConfig.description = config.urlConnection.description;
    }

    return tomlConfig;
  },

  /**
   * Get database type string for db.toml API
   */
  getDbTypeForApi: (type: DatabaseType): string => {
    switch (type) {
      case DatabaseType.PostgreSQL:
        return 'postgres';
      case DatabaseType.MySQL:
        return 'mysql';
      case DatabaseType.Snowflake:
        return 'snowflake';
      case DatabaseType.Databricks:
        return 'databricks';
      default:
        return 'postgres';
    }
  },

  /**
   * Save configurations to db.toml via backend API
   */
  saveConfigurationsToStateDB: async (): Promise<void> => {
    try {
      const state = DatabaseStateService.getState();

      if (state.configurations.length === 0) {
        console.log('[DatabaseStateService] No configurations to save');
        return;
      }

      // Get existing configs from db.toml to determine what to add/update/remove
      const existingConfigs = await StateDBCachingService.getDatabaseConfigs();
      const existingNames = new Set(existingConfigs.map((c: any) => `${c.type}:${c.name}`));
      const currentNames = new Set<string>();

      // Save each configuration to db.toml
      for (const config of state.configurations) {
        const dbType = DatabaseStateService.getDbTypeForApi(config.type);
        const tomlConfig = DatabaseStateService.convertConfigToTomlFormat(config);
        const configKey = `${dbType}:${config.name}`;
        currentNames.add(configKey);

        if (existingNames.has(configKey)) {
          // Update existing config
          await StateDBCachingService.updateDatabaseConfig(
            dbType,
            config.name,
            tomlConfig
          );
        } else {
          // Add new config
          await StateDBCachingService.addDatabaseConfig(dbType, tomlConfig);
        }
      }

      // Remove configs that no longer exist in state
      for (const existing of existingConfigs) {
        const configKey = `${existing.type}:${existing.name}`;
        if (!currentNames.has(configKey)) {
          await StateDBCachingService.deleteDatabaseConfig(
            existing.type,
            existing.name
          );
        }
      }

      // Also save schema cache separately in app_values (schemas are too large for TOML)
      const schemaCache = state.configurations
        .filter(c => c.database_schema)
        .reduce((acc, c) => {
          acc[c.id] = {
            schema_last_updated: c.schema_last_updated,
            database_schema: c.database_schema
          };
          return acc;
        }, {} as Record<string, any>);

      if (Object.keys(schemaCache).length > 0) {
        await StateDBCachingService.setObjectValue('database_schema_cache', schemaCache);
      }

      console.log(
        '[DatabaseStateService] ✅ Configurations saved to db.toml'
      );
    } catch (error) {
      console.error(
        '[DatabaseStateService] ❌ Failed to save configurations to db.toml:',
        error
      );
      throw error;
    }
  },

  /**
   * Convert db.toml format back to internal IDatabaseConfig format
   */
  convertTomlToConfig: (tomlConfig: any): IDatabaseConfig | null => {
    try {
      const dbType = tomlConfig.type || 'postgres';
      const now = new Date().toISOString();

      // Map db type string to enum
      let type: DatabaseType;
      switch (dbType) {
        case 'postgres':
          type = DatabaseType.PostgreSQL;
          break;
        case 'mysql':
          type = DatabaseType.MySQL;
          break;
        case 'snowflake':
          type = DatabaseType.Snowflake;
          break;
        case 'databricks':
          type = DatabaseType.Databricks;
          break;
        default:
          type = DatabaseType.PostgreSQL;
      }

      const config: IDatabaseConfig = {
        id: tomlConfig.id || uuidv4(),
        name: tomlConfig.name,
        type,
        connectionType: tomlConfig.connection_url ? 'url' : 'credentials',
        createdAt: tomlConfig.createdAt || now,
        updatedAt: tomlConfig.updatedAt || now
      };

      // Build credentials based on type
      if (!tomlConfig.connection_url) {
        if (type === DatabaseType.Snowflake) {
          config.credentials = {
            id: config.id,
            name: config.name,
            description: tomlConfig.description || '',
            type: DatabaseType.Snowflake,
            host: tomlConfig.host || '',
            port: tomlConfig.port || 443,
            database: tomlConfig.database || '',
            username: tomlConfig.username || '',
            password: tomlConfig.password || '',
            connectionUrl: tomlConfig.account || '',
            warehouse: tomlConfig.warehouse,
            role: tomlConfig.role,
            createdAt: now,
            updatedAt: now
          } as ISnowflakeCredentials;
        } else if (type === DatabaseType.Databricks) {
          config.credentials = {
            id: config.id,
            name: config.name,
            description: tomlConfig.description || '',
            type: DatabaseType.Databricks,
            host: tomlConfig.host || '',
            port: tomlConfig.port || 443,
            database: tomlConfig.database || '',
            username: tomlConfig.username || '',
            password: tomlConfig.password || '',
            connectionUrl: tomlConfig.host || '',
            authType: tomlConfig.auth_type || 'pat',
            accessToken: tomlConfig.access_token,
            catalog: tomlConfig.catalog || '',
            warehouseHttpPath: tomlConfig.http_path,
            createdAt: now,
            updatedAt: now
          } as IDatabricksCredentials;
        } else {
          // MySQL or PostgreSQL
          const baseCreds: IDatabaseCredentials = {
            id: config.id,
            name: config.name,
            description: tomlConfig.description || '',
            type,
            host: tomlConfig.host || '',
            port: tomlConfig.port || (type === DatabaseType.MySQL ? 3306 : 5432),
            database: tomlConfig.database || '',
            username: tomlConfig.username || '',
            password: tomlConfig.password || '',
            createdAt: now,
            updatedAt: now
          };
          if (type === DatabaseType.MySQL) {
            config.credentials = baseCreds as IMySQLCredentials;
          } else {
            config.credentials = baseCreds as IPostgreSQLCredentials;
          }
        }
      } else {
        config.urlConnection = {
          id: config.id,
          name: config.name,
          description: tomlConfig.description || '',
          type,
          connectionUrl: tomlConfig.connection_url,
          createdAt: now,
          updatedAt: now
        };
      }

      return config;
    } catch (error) {
      console.warn('[DatabaseStateService] Failed to convert TOML config:', tomlConfig, error);
      return null;
    }
  },

  /**
   * Load configurations from db.toml via backend API
   */
  loadConfigurationsFromStateDB: async (): Promise<void> => {
    try {
      // Load configs from db.toml
      const tomlConfigs = await StateDBCachingService.getDatabaseConfigs();

      if (tomlConfigs.length === 0) {
        console.log(
          '[DatabaseStateService] No configurations found in db.toml'
        );
        return;
      }

      // Convert each TOML config to internal format
      const configs = tomlConfigs
        .map((tomlConfig: any) => DatabaseStateService.convertTomlToConfig(tomlConfig))
        .filter((config): config is IDatabaseConfig => config !== null);

      // Load schema cache from app_values
      const schemaCache = await StateDBCachingService.getObjectValue<Record<string, any>>(
        'database_schema_cache',
        {}
      );

      // Merge schema cache back into configs
      for (const config of configs) {
        if (schemaCache[config.id]) {
          config.schema_last_updated = schemaCache[config.id].schema_last_updated;
          config.database_schema = schemaCache[config.id].database_schema;
        }
      }

      // Update state
      DatabaseStateService.setState({ configurations: configs });
      console.log(
        '[DatabaseStateService] ✅ Configurations loaded from db.toml'
      );
    } catch (error) {
      console.error(
        '[DatabaseStateService] ❌ Failed to load configurations from db.toml:',
        error
      );
      throw error;
    }
  },

  /**
   * Create and persist a PostgreSQL configuration with encoding
   */
  createAndPersistPostgreSQLConfig: async (
    name: string,
    description: string,
    host: string,
    port: number,
    database: string,
    username: string,
    password: string
  ): Promise<IDatabaseConfig> => {
    try {
      // Create the configuration
      const config = DatabaseStateService.createPostgreSQLConfig(
        name,
        description,
        host,
        port,
        database,
        username,
        password
      );

      // Save to StateDB
      await DatabaseStateService.saveConfigurationsToStateDB();

      console.log(
        '[DatabaseStateService] ✅ PostgreSQL configuration created and persisted'
      );
      return config;
    } catch (error) {
      console.error(
        '[DatabaseStateService] ❌ Failed to create and persist PostgreSQL config:',
        error
      );
      throw error;
    }
  },

  /**
   * Create and persist a Snowflake configuration with encoding
   */
  createAndPersistSnowflakeConfig: async (
    name: string,
    description: string,
    connectionUrl: string,
    username: string,
    password: string,
    database?: string,
    warehouse?: string,
    role?: string
  ): Promise<IDatabaseConfig> => {
    try {
      // Create the configuration
      const config = DatabaseStateService.createSnowflakeConfig(
        name,
        description,
        connectionUrl,
        username,
        password,
        database,
        warehouse,
        role
      );

      // Save to StateDB
      await DatabaseStateService.saveConfigurationsToStateDB();

      console.log(
        '[DatabaseStateService] ✅ Snowflake configuration created and persisted'
      );
      return config;
    } catch (error) {
      console.error(
        '[DatabaseStateService] ❌ Failed to create and persist Snowflake config:',
        error
      );
      throw error;
    }
  },

  /**
   * Create and persist a MySQL configuration with encoding
   */
  createAndPersistMySQLConfig: async (
    name: string,
    description: string,
    host: string,
    port: number,
    database: string,
    username: string,
    password: string
  ): Promise<IDatabaseConfig> => {
    try {
      // Create the configuration
      const config = DatabaseStateService.createMySQLConfig(
        name,
        description,
        host,
        port,
        database,
        username,
        password
      );

      // Save to StateDB
      await DatabaseStateService.saveConfigurationsToStateDB();

      console.log(
        '[DatabaseStateService] ✅ MySQL configuration created and persisted'
      );
      return config;
    } catch (error) {
      console.error(
        '[DatabaseStateService] ❌ Failed to create and persist MySQL config:',
        error
      );
      throw error;
    }
  },

  /**
   * Create and persist a Databricks configuration with encoding
   */
  createAndPersistDatabricksConfig: async (
    name: string,
    description: string,
    connectionUrl: string,
    authType: DatabricksAuthType,
    catalog: string,
    accessToken?: string,
    clientId?: string,
    clientSecret?: string,
    warehouseHttpPath?: string,
    dbSchema?: string
  ): Promise<IDatabaseConfig> => {
    try {
      // Create the configuration
      const config = DatabaseStateService.createDatabricksConfig(
        name,
        description,
        connectionUrl,
        authType,
        catalog,
        accessToken,
        clientId,
        clientSecret,
        warehouseHttpPath,
        dbSchema
      );

      // Save to StateDB
      await DatabaseStateService.saveConfigurationsToStateDB();

      console.log(
        '[DatabaseStateService] ✅ Databricks configuration created and persisted'
      );
      return config;
    } catch (error) {
      console.error(
        '[DatabaseStateService] ❌ Failed to create and persist Databricks config:',
        error
      );
      throw error;
    }
  },

  /**
   * Remove configuration and update StateDB
   */
  removeConfigurationAndPersist: async (configId: string): Promise<boolean> => {
    try {
      const removed = DatabaseStateService.removeConfiguration(configId);

      if (removed) {
        await DatabaseStateService.saveConfigurationsToStateDB();
        console.log(
          '[DatabaseStateService] ✅ Configuration removed and persisted'
        );
      }

      return removed;
    } catch (error) {
      console.error(
        '[DatabaseStateService] ❌ Failed to remove and persist configuration:',
        error
      );
      throw error;
    }
  },

  /**
   * Update and persist a database configuration
   */
  updateConfigurationAndPersist: async (
    configId: string,
    updates: Partial<IDatabaseConfig>
  ): Promise<boolean> => {
    try {
      const updated = DatabaseStateService.updateConfiguration(
        configId,
        updates
      );

      if (updated) {
        await DatabaseStateService.saveConfigurationsToStateDB();
        console.log(
          '[DatabaseStateService] ✅ Configuration updated and persisted'
        );
      }

      return updated;
    } catch (error) {
      console.error(
        '[DatabaseStateService] ❌ Failed to update and persist configuration:',
        error
      );
      throw error;
    }
  },

  /**
   * Update a database configuration from form data and persist
   */
  updateConfigurationFromFormDataAndPersist: async (
    configId: string,
    name: string,
    description: string,
    type: DatabaseType,
    connectionMethod: 'credentials' | 'url',
    host?: string,
    port?: number,
    database?: string,
    username?: string,
    password?: string,
    connectionUrl?: string,
    warehouse?: string,
    account?: string,
    role?: string,
    // Databricks-specific fields
    databricksAuthType?: DatabricksAuthType,
    databricksAccessToken?: string,
    databricksClientId?: string,
    databricksClientSecret?: string,
    databricksWarehouseHttpPath?: string,
    databricksCatalog?: string,
    databricksSchema?: string
  ): Promise<boolean> => {
    try {
      const currentConfig = DatabaseStateService.getConfiguration(configId);
      if (!currentConfig) {
        return false;
      }

      // Prepare the updated configuration
      const updatedAt = new Date().toISOString();

      let updatedConfig: IDatabaseConfig;

      if (connectionMethod === 'url' && connectionUrl) {
        // URL-based configuration
        updatedConfig = {
          ...currentConfig,
          name,
          type,
          connectionType: 'url',
          credentials: undefined,
          urlConnection: {
            id: currentConfig.id,
            name,
            description,
            type,
            connectionUrl,
            createdAt: currentConfig.createdAt,
            updatedAt
          },
          updatedAt
        };
      } else {
        // Credentials-based configuration
        let credentials:
          | IMySQLCredentials
          | IPostgreSQLCredentials
          | ISnowflakeCredentials
          | IDatabricksCredentials;

        if (type === DatabaseType.Snowflake) {
          // Snowflake credentials with proper defaults
          credentials = {
            id: currentConfig.id,
            name,
            description,
            type: DatabaseType.Snowflake,
            host: '', // Not used for Snowflake
            port: 443,
            database: database || '',
            username: username!,
            password: password!,
            connectionUrl: connectionUrl!,
            warehouse: warehouse || undefined,
            role: role || undefined,
            createdAt: currentConfig.createdAt,
            updatedAt
          } as ISnowflakeCredentials;
        } else if (type === DatabaseType.Databricks) {
          // Databricks credentials
          const authType = databricksAuthType || 'pat';
          credentials = {
            id: currentConfig.id,
            name,
            description,
            type: DatabaseType.Databricks,
            host: '', // Not used for Databricks
            port: 443,
            database: databricksCatalog || '',
            username: authType === 'pat' ? 'token' : databricksClientId || '',
            password:
              authType === 'pat'
                ? databricksAccessToken || ''
                : databricksClientSecret || '',
            connectionUrl: connectionUrl!,
            authType,
            accessToken: authType === 'pat' ? databricksAccessToken : undefined,
            clientId:
              authType === 'service_principal' ? databricksClientId : undefined,
            clientSecret:
              authType === 'service_principal'
                ? databricksClientSecret
                : undefined,
            warehouseHttpPath: databricksWarehouseHttpPath,
            catalog: databricksCatalog!,
            schema: databricksSchema,
            createdAt: currentConfig.createdAt,
            updatedAt
          } as IDatabricksCredentials;
        } else {
          // MySQL/PostgreSQL credentials
          const baseCredentials = {
            id: currentConfig.id,
            name,
            description,
            type,
            host: host!,
            port: port!,
            database: database!,
            username: username!,
            password: password!,
            createdAt: currentConfig.createdAt,
            updatedAt
          };

          if (type === DatabaseType.MySQL) {
            credentials = {
              ...baseCredentials,
              type: DatabaseType.MySQL
            } as IMySQLCredentials;
          } else {
            credentials = {
              ...baseCredentials,
              type: DatabaseType.PostgreSQL
            } as IPostgreSQLCredentials;
          }
        }

        updatedConfig = {
          ...currentConfig,
          name,
          type,
          connectionType: 'credentials',
          credentials,
          urlConnection: undefined,
          updatedAt
        };
      }

      // Update and persist
      const updated = DatabaseStateService.updateConfiguration(
        configId,
        updatedConfig
      );

      if (updated) {
        await DatabaseStateService.saveConfigurationsToStateDB();
        console.log(
          '[DatabaseStateService] ✅ Configuration updated from form data and persisted'
        );
      }

      return updated;
    } catch (error) {
      console.error(
        '[DatabaseStateService] ❌ Failed to update configuration from form data:',
        error
      );
      throw error;
    }
  },

  /**
   * Initialize service and load configurations from StateDB
   */
  initializeWithStateDB: async (): Promise<void> => {
    try {
      DatabaseStateService.initialize();
      await DatabaseStateService.loadConfigurationsFromStateDB();
      console.log(
        '[DatabaseStateService] ✅ Service initialized with StateDB data'
      );
    } catch (error) {
      console.error(
        '[DatabaseStateService] ❌ Failed to initialize with StateDB:',
        error
      );
      // Continue initialization even if loading fails
      DatabaseStateService.initialize();
    }
  }
};
