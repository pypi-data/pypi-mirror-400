"""
Database Configuration Service
Manages database configurations stored in db.toml in the connect/ cache directory
"""

import logging
from typing import Any, Dict, List, Optional

from .signalpilot_home import get_signalpilot_home

logger = logging.getLogger(__name__)


class DatabaseConfigService:
    """
    Service for managing database configurations in TOML format.
    Configurations stored at <cache_dir>/connect/db.toml
    (e.g., ~/Library/Caches/SignalPilotAI/connect/db.toml on macOS)
    """

    _instance = None

    # Supported database types
    SUPPORTED_TYPES = ["snowflake", "postgres", "mysql", "databricks"]

    def __init__(self):
        self._home_manager = get_signalpilot_home()

    @classmethod
    def get_instance(cls) -> 'DatabaseConfigService':
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = DatabaseConfigService()
        return cls._instance

    def get_all_configs(self) -> List[Dict[str, Any]]:
        """Get all database configurations."""
        return self._home_manager.get_database_configs()

    def get_config(self, db_type: str, name: str) -> Optional[Dict[str, Any]]:
        """Get a specific database configuration."""
        return self._home_manager.get_database_config(db_type, name)

    def get_configs_by_type(self, db_type: str) -> List[Dict[str, Any]]:
        """Get all configurations for a specific database type."""
        configs = self.get_all_configs()
        return [c for c in configs if c.get("type") == db_type]

    def add_config(self, db_type: str, config: Dict[str, Any]) -> bool:
        """Add a new database configuration."""
        if db_type not in self.SUPPORTED_TYPES:
            logger.error(f"Unsupported database type: {db_type}")
            return False

        if "name" not in config:
            logger.error("Database config must have a 'name' field")
            return False

        return self._home_manager.add_database_config(db_type, config)

    def update_config(self, db_type: str, name: str,
                      updates: Dict[str, Any]) -> bool:
        """Update an existing database configuration."""
        return self._home_manager.update_database_config(db_type, name, updates)

    def remove_config(self, db_type: str, name: str) -> bool:
        """Remove a database configuration."""
        return self._home_manager.remove_database_config(db_type, name)

    def set_defaults(self, defaults: Dict[str, Any]) -> bool:
        """Set global defaults for database configurations."""
        return self._home_manager.set_database_defaults(defaults)

    def get_defaults(self) -> Dict[str, Any]:
        """Get global defaults."""
        return self._home_manager.get_database_defaults()

    # ==================== Type-specific helpers ====================

    def add_snowflake_config(self, name: str, account: str,
                             database: str = None,
                             warehouse: str = None,
                             role: str = None,
                             username: str = None,
                             password: str = None,
                             **extra) -> bool:
        """Add a Snowflake database configuration."""
        config = {
            "name": name,
            "account": account,
        }
        if database:
            config["database"] = database
        if warehouse:
            config["warehouse"] = warehouse
        if role:
            config["role"] = role
        if username:
            config["username"] = username
        if password:
            config["password"] = password
        config.update(extra)

        return self.add_config("snowflake", config)

    def add_postgres_config(self, name: str, host: str, port: int,
                            database: str, username: str, password: str,
                            **extra) -> bool:
        """Add a PostgreSQL database configuration."""
        config = {
            "name": name,
            "host": host,
            "port": port,
            "database": database,
            "username": username,
            "password": password,
        }
        config.update(extra)

        return self.add_config("postgres", config)

    def add_mysql_config(self, name: str, host: str, port: int,
                         database: str, username: str, password: str,
                         **extra) -> bool:
        """Add a MySQL database configuration."""
        config = {
            "name": name,
            "host": host,
            "port": port,
            "database": database,
            "username": username,
            "password": password,
        }
        config.update(extra)

        return self.add_config("mysql", config)

    def add_databricks_config(self, name: str, host: str,
                              http_path: str, catalog: str,
                              auth_type: str = "pat",
                              access_token: str = None,
                              client_id: str = None,
                              client_secret: str = None,
                              **extra) -> bool:
        """Add a Databricks database configuration."""
        config = {
            "name": name,
            "host": host,
            "http_path": http_path,
            "catalog": catalog,
            "auth_type": auth_type,
        }
        if access_token:
            config["access_token"] = access_token
        if client_id:
            config["client_id"] = client_id
        if client_secret:
            config["client_secret"] = client_secret
        config.update(extra)

        return self.add_config("databricks", config)


def get_database_config_service() -> DatabaseConfigService:
    """Get the singleton instance."""
    return DatabaseConfigService.get_instance()
