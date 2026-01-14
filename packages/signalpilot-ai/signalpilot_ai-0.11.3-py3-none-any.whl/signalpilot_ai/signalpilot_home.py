"""
SignalPilotHomeManager - Centralized configuration management for connect/ folder

The connect/ folder is stored in the OS-specific cache directory:
- macOS: ~/Library/Caches/SignalPilotAI/connect/
- Windows: %LOCALAPPDATA%/SignalPilotAI/Cache/connect/
- Linux: ~/.cache/signalpilot-ai/connect/

Provides unified access to:
- mcp.json - MCP server configurations
- db.toml - Database configurations
- .env - OAuth tokens
"""

import json
import logging
import os
import platform
import shutil
import sys
import tempfile
import threading
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

# TOML reading - tomllib is built-in for Python 3.11+
if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

logger = logging.getLogger(__name__)


def _get_cache_base_directory() -> Path:
    """Get the OS-specific cache directory for SignalPilotAI."""
    system = platform.system().lower()

    try:
        if system == "windows":
            appdata_local = os.environ.get('LOCALAPPDATA')
            if appdata_local:
                return Path(appdata_local) / "SignalPilotAI" / "Cache"
            appdata_roaming = os.environ.get('APPDATA')
            if appdata_roaming:
                return Path(appdata_roaming) / "SignalPilotAI" / "Cache"
            userprofile = os.environ.get('USERPROFILE')
            if userprofile:
                return Path(userprofile) / ".signalpilot-cache"

        elif system == "darwin":  # macOS
            return Path.home() / "Library" / "Caches" / "SignalPilotAI"

        else:  # Linux and other Unix-like
            cache_home = os.environ.get('XDG_CACHE_HOME')
            if cache_home:
                return Path(cache_home) / "signalpilot-ai"
            return Path.home() / ".cache" / "signalpilot-ai"

    except Exception as e:
        logger.error(f"Error determining cache directory: {e}")

    # Fallback
    return Path(tempfile.gettempdir()) / f"signalpilot-ai-{os.getuid() if hasattr(os, 'getuid') else 'user'}"


def _format_toml_value(value: Any) -> str:
    """Format a Python value as a TOML value string."""
    if value is None:
        return '""'
    elif isinstance(value, bool):
        return "true" if value else "false"
    elif isinstance(value, int):
        return str(value)
    elif isinstance(value, float):
        return str(value)
    elif isinstance(value, str):
        # Check if multiline
        if '\n' in value:
            # Use multiline basic string
            escaped = value.replace('\\', '\\\\').replace('"""', '\\"\\"\\"')
            return f'"""{escaped}"""'
        else:
            # Use basic string with escaping
            escaped = value.replace('\\', '\\\\').replace('"', '\\"')
            return f'"{escaped}"'
    elif isinstance(value, list):
        items = [_format_toml_value(v) for v in value]
        return f"[{', '.join(items)}]"
    else:
        # Fallback to string representation
        return f'"{str(value)}"'


def _write_toml(data: Dict[str, Any]) -> str:
    """
    Simple TOML writer for our specific use case.
    Handles: [defaults], [defaults.type], [[type]] arrays of tables
    """
    lines = []

    # Write defaults section first if present
    defaults = data.get("defaults", {})
    if defaults:
        lines.append("[defaults]")
        for key, value in defaults.items():
            if isinstance(value, dict):
                # Will be written as [defaults.key] later
                continue
            lines.append(f"{key} = {_format_toml_value(value)}")
        lines.append("")

        # Write nested defaults like [defaults.snowflake]
        for key, value in defaults.items():
            if isinstance(value, dict):
                lines.append(f"[defaults.{key}]")
                for k, v in value.items():
                    lines.append(f"{k} = {_format_toml_value(v)}")
                lines.append("")

    # Write array of tables for each database type
    for db_type in ["snowflake", "postgres", "mysql", "databricks"]:
        if db_type in data and data[db_type]:
            for entry in data[db_type]:
                lines.append(f"[[{db_type}]]")
                for key, value in entry.items():
                    if not isinstance(value, (dict, list)) or isinstance(value, list):
                        lines.append(f"{key} = {_format_toml_value(value)}")
                lines.append("")

    return "\n".join(lines)


class SignalPilotHomeManager:
    """
    Centralized manager for SignalPilot configuration files.
    All configs stored in the OS-specific cache directory under connect/
    (e.g., ~/Library/Caches/SignalPilotAI/connect/ on macOS)
    """

    _instance = None
    _lock = threading.Lock()

    # Directory structure
    CONNECT_DIR_NAME = "connect"

    # File names
    MCP_CONFIG_FILE = "mcp.json"
    DB_CONFIG_FILE = "db.toml"
    ENV_FILE = ".env"

    def __init__(self):
        self._base_path: Optional[Path] = None
        self._connect_path: Optional[Path] = None
        self._file_lock = threading.RLock()
        self._setup_directories()

    @classmethod
    def get_instance(cls) -> 'SignalPilotHomeManager':
        """Get singleton instance (thread-safe)."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = SignalPilotHomeManager()
        return cls._instance

    def _setup_directories(self):
        """Create connect/ directory in the OS-specific cache location."""
        self._base_path = _get_cache_base_directory()
        self._connect_path = self._base_path / self.CONNECT_DIR_NAME

        try:
            self._connect_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"[SignalPilotHomeManager] Using directory: {self._connect_path}")
        except Exception as e:
            logger.error(f"[SignalPilotHomeManager] Error creating directory: {e}")

    # ==================== Path Accessors ====================

    @property
    def base_path(self) -> Path:
        """Get the cache base directory (e.g., ~/Library/Caches/SignalPilotAI on macOS)"""
        return self._base_path

    @property
    def connect_path(self) -> Path:
        """Get the connect directory (e.g., ~/Library/Caches/SignalPilotAI/connect on macOS)"""
        return self._connect_path

    @property
    def mcp_config_path(self) -> Path:
        """Get path to mcp.json"""
        return self._connect_path / self.MCP_CONFIG_FILE

    @property
    def db_config_path(self) -> Path:
        """Get path to db.toml"""
        return self._connect_path / self.DB_CONFIG_FILE

    @property
    def env_path(self) -> Path:
        """Get path to .env"""
        return self._connect_path / self.ENV_FILE

    # ==================== Safe File Operations ====================

    def _safe_write_json(self, file_path: Path, data: Any, max_retries: int = 3) -> bool:
        """Safely write JSON data with atomic operations."""
        with self._file_lock:
            if not file_path.parent.exists():
                try:
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                except Exception as e:
                    logger.error(f"Failed to create directory {file_path.parent}: {e}")
                    return False

            for attempt in range(max_retries):
                temp_path = file_path.with_suffix(f".tmp.{uuid.uuid4().hex[:8]}")

                try:
                    # Write to temporary file first
                    with open(temp_path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)

                    # Verify the written data
                    with open(temp_path, 'r', encoding='utf-8') as f:
                        json.load(f)

                    # Atomic move to final location
                    if platform.system().lower() == "windows":
                        if file_path.exists():
                            file_path.unlink()

                    shutil.move(str(temp_path), str(file_path))
                    return True

                except Exception as e:
                    logger.error(f"Write attempt {attempt + 1} failed for {file_path}: {e}")

                    try:
                        if temp_path.exists():
                            temp_path.unlink()
                    except:
                        pass

                    if attempt < max_retries - 1:
                        time.sleep(0.1 * (attempt + 1))

            return False

    def _safe_read_json(self, file_path: Path, default: Any = None) -> Any:
        """Safely read JSON data."""
        if not file_path.exists():
            return default

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to read {file_path}: {e}")
            return default

    def _safe_write_toml(self, file_path: Path, data: Dict[str, Any], max_retries: int = 3) -> bool:
        """Safely write TOML data with atomic operations."""
        with self._file_lock:
            if not file_path.parent.exists():
                try:
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                except Exception as e:
                    logger.error(f"Failed to create directory {file_path.parent}: {e}")
                    return False

            for attempt in range(max_retries):
                temp_path = file_path.with_suffix(f".tmp.{uuid.uuid4().hex[:8]}")

                try:
                    # Format TOML content
                    toml_content = _write_toml(data)

                    # Write to temporary file first
                    with open(temp_path, 'w', encoding='utf-8') as f:
                        f.write(toml_content)

                    # Verify the written data can be read back
                    with open(temp_path, 'rb') as f:
                        tomllib.load(f)

                    # Atomic move to final location
                    if platform.system().lower() == "windows":
                        if file_path.exists():
                            file_path.unlink()

                    shutil.move(str(temp_path), str(file_path))
                    return True

                except Exception as e:
                    logger.error(f"TOML write attempt {attempt + 1} failed for {file_path}: {e}")

                    try:
                        if temp_path.exists():
                            temp_path.unlink()
                    except:
                        pass

                    if attempt < max_retries - 1:
                        time.sleep(0.1 * (attempt + 1))

            return False

    def _safe_read_toml(self, file_path: Path, default: Any = None) -> Any:
        """Safely read TOML data."""
        if not file_path.exists():
            return default

        try:
            with open(file_path, 'rb') as f:
                return tomllib.load(f)
        except Exception as e:
            logger.error(f"Failed to read TOML {file_path}: {e}")
            return default

    # ==================== MCP Config (JSON) ====================

    def read_mcp_config(self) -> Dict[str, Any]:
        """Read mcp.json configuration."""
        return self._safe_read_json(self.mcp_config_path, {"mcpServers": {}})

    def write_mcp_config(self, config: Dict[str, Any]) -> bool:
        """Write mcp.json configuration."""
        return self._safe_write_json(self.mcp_config_path, config)

    def get_mcp_servers(self) -> Dict[str, Any]:
        """Get all MCP servers from config."""
        config = self.read_mcp_config()
        return config.get("mcpServers", {})

    def set_mcp_server(self, server_id: str, server_config: Dict[str, Any]) -> bool:
        """Set/update a single MCP server."""
        config = self.read_mcp_config()
        if "mcpServers" not in config:
            config["mcpServers"] = {}
        config["mcpServers"][server_id] = server_config
        return self.write_mcp_config(config)

    def remove_mcp_server(self, server_id: str) -> bool:
        """Remove an MCP server."""
        config = self.read_mcp_config()
        servers = config.get("mcpServers", {})
        if server_id in servers:
            del servers[server_id]
            config["mcpServers"] = servers
            return self.write_mcp_config(config)
        return True

    # ==================== DB Config (TOML) ====================

    def read_db_config(self) -> Dict[str, Any]:
        """Read db.toml configuration."""
        return self._safe_read_toml(self.db_config_path, {"defaults": {}})

    def write_db_config(self, config: Dict[str, Any]) -> bool:
        """Write db.toml configuration."""
        return self._safe_write_toml(self.db_config_path, config)

    def get_database_configs(self) -> List[Dict[str, Any]]:
        """Get all database configurations from db.toml."""
        config = self.read_db_config()
        defaults = config.get("defaults", {})

        databases = []
        for db_type in ["snowflake", "postgres", "mysql", "databricks"]:
            if db_type in config:
                type_defaults = defaults.get(db_type, {})
                global_defaults = {k: v for k, v in defaults.items()
                                   if not isinstance(v, dict)}

                for db_config in config[db_type]:
                    # Merge: global defaults < type defaults < specific config
                    merged = {**global_defaults, **type_defaults, **db_config}
                    merged["type"] = db_type
                    databases.append(merged)

        return databases

    def get_database_config(self, db_type: str, name: str) -> Optional[Dict[str, Any]]:
        """Get a specific database configuration."""
        configs = self.get_database_configs()
        for config in configs:
            if config.get("type") == db_type and config.get("name") == name:
                return config
        return None

    def add_database_config(self, db_type: str, config: Dict[str, Any]) -> bool:
        """Add a new database configuration to db.toml."""
        full_config = self.read_db_config()

        if db_type not in full_config:
            full_config[db_type] = []

        # Check for duplicate name
        for existing in full_config[db_type]:
            if existing.get("name") == config.get("name"):
                logger.error(f"Database config with name '{config.get('name')}' already exists")
                return False

        full_config[db_type].append(config)
        return self.write_db_config(full_config)

    def update_database_config(self, db_type: str, name: str,
                               updates: Dict[str, Any]) -> bool:
        """Update an existing database configuration."""
        full_config = self.read_db_config()

        if db_type not in full_config:
            return False

        for i, db in enumerate(full_config[db_type]):
            if db.get("name") == name:
                full_config[db_type][i] = {**db, **updates}
                return self.write_db_config(full_config)

        return False

    def remove_database_config(self, db_type: str, name: str) -> bool:
        """Remove a database configuration."""
        full_config = self.read_db_config()

        if db_type not in full_config:
            return False

        original_len = len(full_config[db_type])
        full_config[db_type] = [
            db for db in full_config[db_type]
            if db.get("name") != name
        ]

        if len(full_config[db_type]) < original_len:
            return self.write_db_config(full_config)
        return False

    def set_database_defaults(self, defaults: Dict[str, Any]) -> bool:
        """Set global defaults for database configurations."""
        full_config = self.read_db_config()
        full_config["defaults"] = defaults
        return self.write_db_config(full_config)

    def get_database_defaults(self) -> Dict[str, Any]:
        """Get global defaults."""
        config = self.read_db_config()
        return config.get("defaults", {})

    # ==================== OAuth Tokens (.env) ====================

    def read_env(self) -> Dict[str, str]:
        """Read .env file as key-value pairs."""
        if not self.env_path.exists():
            return {}

        env_vars = {}
        try:
            with open(self.env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, _, value = line.partition('=')
                        # Remove quotes if present
                        value = value.strip()
                        if (value.startswith('"') and value.endswith('"')) or \
                           (value.startswith("'") and value.endswith("'")):
                            value = value[1:-1]
                        env_vars[key.strip()] = value
        except Exception as e:
            logger.error(f"[SignalPilotHomeManager] Error reading .env: {e}")

        return env_vars

    def write_env(self, env_vars: Dict[str, str]) -> bool:
        """Write .env file from key-value pairs."""
        with self._file_lock:
            try:
                temp_path = self.env_path.with_suffix(f".tmp.{uuid.uuid4().hex[:8]}")

                with open(temp_path, 'w', encoding='utf-8') as f:
                    f.write("# SignalPilot OAuth Tokens\n")
                    f.write("# Auto-generated - do not edit manually\n\n")

                    for key in sorted(env_vars.keys()):
                        value = env_vars[key]
                        # Quote values containing spaces, quotes, or special chars
                        if any(c in value for c in ' "\'\n\r\t#'):
                            # Escape existing quotes and wrap in quotes
                            value = value.replace('\\', '\\\\').replace('"', '\\"')
                            value = f'"{value}"'
                        f.write(f"{key}={value}\n")

                # Atomic move
                if platform.system().lower() == "windows":
                    if self.env_path.exists():
                        self.env_path.unlink()

                shutil.move(str(temp_path), str(self.env_path))
                return True

            except Exception as e:
                logger.error(f"[SignalPilotHomeManager] Error writing .env: {e}")
                try:
                    if temp_path.exists():
                        temp_path.unlink()
                except:
                    pass
                return False

    def _get_env_prefix(self, server_id: str) -> str:
        """Generate env variable prefix for a server ID."""
        # Convert server-id to OAUTH_SERVER_ID_
        safe_id = server_id.upper().replace('-', '_').replace('.', '_')
        return f"OAUTH_{safe_id}_"

    def get_oauth_tokens(self, server_id: str) -> Optional[Dict[str, str]]:
        """Get OAuth tokens for a specific MCP server."""
        env_vars = self.read_env()
        prefix = self._get_env_prefix(server_id)

        tokens = {}
        for key, value in env_vars.items():
            if key.startswith(prefix):
                # Remove prefix to get original token name
                token_name = key[len(prefix):]
                tokens[token_name] = value

        return tokens if tokens else None

    def set_oauth_tokens(self, server_id: str, tokens: Dict[str, str]) -> bool:
        """Set OAuth tokens for an MCP server."""
        env_vars = self.read_env()
        prefix = self._get_env_prefix(server_id)

        # Remove existing tokens for this server
        env_vars = {k: v for k, v in env_vars.items()
                    if not k.startswith(prefix)}

        # Add new tokens
        for token_name, value in tokens.items():
            env_vars[f"{prefix}{token_name}"] = value

        return self.write_env(env_vars)

    def remove_oauth_tokens(self, server_id: str) -> bool:
        """Remove OAuth tokens for an MCP server."""
        env_vars = self.read_env()
        prefix = self._get_env_prefix(server_id)

        new_env = {k: v for k, v in env_vars.items()
                   if not k.startswith(prefix)}

        if len(new_env) < len(env_vars):
            return self.write_env(new_env)
        return True  # Nothing to remove

    def get_oauth_registry(self) -> Dict[str, str]:
        """Get mapping of server IDs to integration IDs from .env registry."""
        env_vars = self.read_env()
        registry = {}

        for key, value in env_vars.items():
            if key.startswith("OAUTH_REGISTRY_"):
                # OAUTH_REGISTRY_SERVER_ID=integration_id
                server_id = key[15:].lower().replace('_', '-')
                registry[server_id] = value

        return registry

    def set_oauth_registry_entry(self, server_id: str, integration_id: str) -> bool:
        """Add an entry to the OAuth registry."""
        env_vars = self.read_env()
        registry_key = f"OAUTH_REGISTRY_{server_id.upper().replace('-', '_')}"
        env_vars[registry_key] = integration_id
        return self.write_env(env_vars)

    def remove_oauth_registry_entry(self, server_id: str) -> bool:
        """Remove an entry from the OAuth registry."""
        env_vars = self.read_env()
        registry_key = f"OAUTH_REGISTRY_{server_id.upper().replace('-', '_')}"

        if registry_key in env_vars:
            del env_vars[registry_key]
            return self.write_env(env_vars)
        return True

    # ==================== Utility Methods ====================

    def is_available(self) -> bool:
        """Check if the SignalPilotHome directory is available."""
        return self._connect_path is not None and self._connect_path.exists()

    def get_info(self) -> Dict[str, Any]:
        """Get information about the SignalPilotHome setup."""
        info = {
            "available": self.is_available(),
            "base_path": str(self._base_path),
            "connect_path": str(self._connect_path),
            "mcp_config_exists": self.mcp_config_path.exists(),
            "db_config_exists": self.db_config_path.exists(),
            "env_exists": self.env_path.exists(),
        }

        if self.is_available():
            try:
                if self.mcp_config_path.exists():
                    info["mcp_config_size"] = self.mcp_config_path.stat().st_size
                    info["mcp_servers_count"] = len(self.get_mcp_servers())

                if self.db_config_path.exists():
                    info["db_config_size"] = self.db_config_path.stat().st_size
                    info["db_configs_count"] = len(self.get_database_configs())

                if self.env_path.exists():
                    info["env_size"] = self.env_path.stat().st_size
                    info["oauth_registry_count"] = len(self.get_oauth_registry())

            except Exception as e:
                info["error"] = str(e)

        return info


# Global instance accessor
def get_signalpilot_home() -> SignalPilotHomeManager:
    """Get the singleton instance."""
    return SignalPilotHomeManager.get_instance()


class UserRulesManager:
    """
    Manager for user-defined rules (snippets) stored as markdown files.
    Rules are stored in ~/SignalPilotHome/user-rules/ as .md files.

    Each rule file follows a format:
    ---
    id: unique-id
    title: Rule Title
    description: Optional description
    created_at: ISO timestamp
    updated_at: ISO timestamp
    ---

    Rule content goes here...
    """

    _instance = None
    _lock = threading.Lock()

    SIGNALPILOT_HOME_DIR = "SignalPilotHome"
    USER_RULES_DIR = "user-rules"

    def __init__(self):
        self._rules_path: Optional[Path] = None
        self._file_lock = threading.RLock()
        self._setup_directory()

    @classmethod
    def get_instance(cls) -> 'UserRulesManager':
        """Get singleton instance (thread-safe)."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = UserRulesManager()
        return cls._instance

    def _setup_directory(self):
        """Create user-rules directory in ~/SignalPilotHome/."""
        try:
            # Use ~/SignalPilotHome/user-rules/
            home_dir = Path.home() / self.SIGNALPILOT_HOME_DIR
            self._rules_path = home_dir / self.USER_RULES_DIR
            self._rules_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"[UserRulesManager] Using directory: {self._rules_path}")
        except Exception as e:
            logger.error(f"[UserRulesManager] Error creating directory: {e}")
            self._rules_path = None

    @property
    def rules_path(self) -> Optional[Path]:
        """Get the user-rules directory path."""
        return self._rules_path

    def _parse_frontmatter(self, content: str) -> tuple[Dict[str, Any], str]:
        """Parse YAML frontmatter from markdown content."""
        if not content.startswith('---'):
            return {}, content

        parts = content.split('---', 2)
        if len(parts) < 3:
            return {}, content

        frontmatter_str = parts[1].strip()
        body = parts[2].strip()

        # Simple YAML parsing for our specific use case
        frontmatter = {}
        for line in frontmatter_str.split('\n'):
            line = line.strip()
            if ':' in line:
                key, _, value = line.partition(':')
                key = key.strip()
                value = value.strip()
                # Remove quotes if present
                if (value.startswith('"') and value.endswith('"')) or \
                   (value.startswith("'") and value.endswith("'")):
                    value = value[1:-1]
                frontmatter[key] = value

        return frontmatter, body

    def _format_frontmatter(self, metadata: Dict[str, Any]) -> str:
        """Format metadata as YAML frontmatter."""
        lines = ['---']
        for key, value in metadata.items():
            if value is not None:
                # Quote strings that contain special characters
                if isinstance(value, str) and any(c in value for c in ':\n"\''):
                    value = f'"{value}"'
                lines.append(f'{key}: {value}')
        lines.append('---')
        return '\n'.join(lines)

    def _sanitize_filename(self, title: str) -> str:
        """Convert title to safe filename."""
        import re
        # Replace spaces with hyphens, remove special characters
        filename = re.sub(r'[^\w\s-]', '', title.lower())
        filename = re.sub(r'[-\s]+', '-', filename).strip('-')
        return filename[:50]  # Limit length

    def list_rules(self) -> List[Dict[str, Any]]:
        """List all user rules."""
        if not self._rules_path or not self._rules_path.exists():
            return []

        rules = []
        try:
            for md_file in sorted(self._rules_path.glob('*.md')):
                try:
                    with open(md_file, 'r', encoding='utf-8') as f:
                        content = f.read()

                    frontmatter, body = self._parse_frontmatter(content)

                    # Use frontmatter id or generate from filename
                    rule_id = frontmatter.get('id', md_file.stem)

                    rules.append({
                        'id': rule_id,
                        'title': frontmatter.get('title', md_file.stem),
                        'description': frontmatter.get('description', ''),
                        'content': body,
                        'created_at': frontmatter.get('created_at', ''),
                        'updated_at': frontmatter.get('updated_at', ''),
                        'filename': md_file.name
                    })
                except Exception as e:
                    logger.error(f"[UserRulesManager] Error reading {md_file}: {e}")
                    continue

        except Exception as e:
            logger.error(f"[UserRulesManager] Error listing rules: {e}")

        return rules

    def get_rule(self, rule_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific rule by ID."""
        rules = self.list_rules()
        for rule in rules:
            if rule['id'] == rule_id:
                return rule
        return None

    def create_rule(self, title: str, content: str, description: str = '',
                    rule_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Create a new rule as a markdown file."""
        if not self._rules_path:
            logger.error("[UserRulesManager] Rules directory not available")
            return None

        with self._file_lock:
            # Generate ID if not provided
            if not rule_id:
                rule_id = f"rule-{uuid.uuid4().hex[:8]}"

            # Generate filename from title
            filename = self._sanitize_filename(title)
            if not filename:
                filename = rule_id

            filepath = self._rules_path / f"{filename}.md"

            # Ensure unique filename
            counter = 1
            while filepath.exists():
                filepath = self._rules_path / f"{filename}-{counter}.md"
                counter += 1

            now = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())

            metadata = {
                'id': rule_id,
                'title': title,
                'description': description,
                'created_at': now,
                'updated_at': now
            }

            frontmatter = self._format_frontmatter(metadata)
            full_content = f"{frontmatter}\n\n{content}"

            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(full_content)

                logger.info(f"[UserRulesManager] Created rule: {filepath}")

                return {
                    'id': rule_id,
                    'title': title,
                    'description': description,
                    'content': content,
                    'created_at': now,
                    'updated_at': now,
                    'filename': filepath.name
                }
            except Exception as e:
                logger.error(f"[UserRulesManager] Error creating rule: {e}")
                return None

    def update_rule(self, rule_id: str, title: Optional[str] = None,
                    content: Optional[str] = None,
                    description: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Update an existing rule."""
        if not self._rules_path:
            return None

        with self._file_lock:
            # Find the rule file
            for md_file in self._rules_path.glob('*.md'):
                try:
                    with open(md_file, 'r', encoding='utf-8') as f:
                        file_content = f.read()

                    frontmatter, body = self._parse_frontmatter(file_content)

                    if frontmatter.get('id') == rule_id:
                        # Update fields
                        if title is not None:
                            frontmatter['title'] = title
                        if description is not None:
                            frontmatter['description'] = description
                        if content is not None:
                            body = content

                        frontmatter['updated_at'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())

                        # Write back
                        new_frontmatter = self._format_frontmatter(frontmatter)
                        full_content = f"{new_frontmatter}\n\n{body}"

                        with open(md_file, 'w', encoding='utf-8') as f:
                            f.write(full_content)

                        logger.info(f"[UserRulesManager] Updated rule: {md_file}")

                        return {
                            'id': rule_id,
                            'title': frontmatter.get('title', ''),
                            'description': frontmatter.get('description', ''),
                            'content': body,
                            'created_at': frontmatter.get('created_at', ''),
                            'updated_at': frontmatter.get('updated_at', ''),
                            'filename': md_file.name
                        }

                except Exception as e:
                    logger.error(f"[UserRulesManager] Error updating {md_file}: {e}")
                    continue

            logger.warning(f"[UserRulesManager] Rule not found: {rule_id}")
            return None

    def delete_rule(self, rule_id: str) -> bool:
        """Delete a rule by ID."""
        if not self._rules_path:
            return False

        with self._file_lock:
            for md_file in self._rules_path.glob('*.md'):
                try:
                    with open(md_file, 'r', encoding='utf-8') as f:
                        content = f.read()

                    frontmatter, _ = self._parse_frontmatter(content)

                    if frontmatter.get('id') == rule_id:
                        md_file.unlink()
                        logger.info(f"[UserRulesManager] Deleted rule: {md_file}")
                        return True

                except Exception as e:
                    logger.error(f"[UserRulesManager] Error checking {md_file}: {e}")
                    continue

        logger.warning(f"[UserRulesManager] Rule not found for deletion: {rule_id}")
        return False

    def migrate_from_json(self, snippets: List[Dict[str, Any]]) -> int:
        """
        Migrate snippets from JSON format to markdown files.
        Returns the number of successfully migrated rules.
        """
        migrated = 0
        for snippet in snippets:
            try:
                rule = self.create_rule(
                    title=snippet.get('title', 'Untitled'),
                    content=snippet.get('content', ''),
                    description=snippet.get('description', ''),
                    rule_id=snippet.get('id')
                )
                if rule:
                    migrated += 1
            except Exception as e:
                logger.error(f"[UserRulesManager] Error migrating snippet: {e}")

        logger.info(f"[UserRulesManager] Migrated {migrated}/{len(snippets)} snippets")
        return migrated

    def is_available(self) -> bool:
        """Check if the user rules directory is available."""
        return self._rules_path is not None and self._rules_path.exists()

    def get_info(self) -> Dict[str, Any]:
        """Get information about the user rules setup."""
        info = {
            "available": self.is_available(),
            "rules_path": str(self._rules_path) if self._rules_path else None,
            "rules_count": 0
        }

        if self.is_available():
            try:
                info["rules_count"] = len(list(self._rules_path.glob('*.md')))
            except Exception as e:
                info["error"] = str(e)

        return info


# Global user rules instance accessor
def get_user_rules_manager() -> UserRulesManager:
    """Get the singleton instance."""
    return UserRulesManager.get_instance()
