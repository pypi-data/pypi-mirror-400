"""
HTTP Handlers for Database Configuration API
Provides REST endpoints for managing db.toml configurations
"""

import json

from jupyter_server.base.handlers import APIHandler
import tornado

from .database_config_service import get_database_config_service


class DatabaseConfigsHandler(APIHandler):
    """Handler for database configuration operations."""

    @tornado.web.authenticated
    def get(self, db_type=None):
        """Get database configurations."""
        try:
            service = get_database_config_service()

            if db_type:
                configs = service.get_configs_by_type(db_type)
            else:
                configs = service.get_all_configs()

            self.finish(json.dumps({
                "configurations": configs,
                "count": len(configs)
            }))
        except Exception as e:
            self.set_status(500)
            self.finish(json.dumps({"error": str(e)}))

    @tornado.web.authenticated
    def post(self, db_type=None):
        """Add a new database configuration."""
        try:
            if not db_type:
                self.set_status(400)
                self.finish(json.dumps({"error": "Database type required in URL path"}))
                return

            body = json.loads(self.request.body.decode('utf-8'))
            service = get_database_config_service()

            success = service.add_config(db_type, body)

            if success:
                self.finish(json.dumps({
                    "success": True,
                    "message": f"Added {db_type} configuration: {body.get('name', 'unnamed')}"
                }))
            else:
                self.set_status(400)
                self.finish(json.dumps({"error": "Failed to add configuration. Check name uniqueness and required fields."}))
        except json.JSONDecodeError as e:
            self.set_status(400)
            self.finish(json.dumps({"error": f"Invalid JSON: {str(e)}"}))
        except Exception as e:
            self.set_status(500)
            self.finish(json.dumps({"error": str(e)}))

    @tornado.web.authenticated
    def put(self, db_type=None):
        """Update a database configuration."""
        try:
            if not db_type:
                self.set_status(400)
                self.finish(json.dumps({"error": "Database type required in URL path"}))
                return

            body = json.loads(self.request.body.decode('utf-8'))
            name = body.pop("name", None)

            if not name:
                self.set_status(400)
                self.finish(json.dumps({"error": "Configuration 'name' required in body"}))
                return

            service = get_database_config_service()
            success = service.update_config(db_type, name, body)

            if success:
                self.finish(json.dumps({
                    "success": True,
                    "message": f"Updated {db_type} configuration: {name}"
                }))
            else:
                self.set_status(404)
                self.finish(json.dumps({"error": f"Configuration '{name}' not found"}))
        except json.JSONDecodeError as e:
            self.set_status(400)
            self.finish(json.dumps({"error": f"Invalid JSON: {str(e)}"}))
        except Exception as e:
            self.set_status(500)
            self.finish(json.dumps({"error": str(e)}))

    @tornado.web.authenticated
    def delete(self, db_type=None):
        """Delete a database configuration."""
        try:
            if not db_type:
                self.set_status(400)
                self.finish(json.dumps({"error": "Database type required in URL path"}))
                return

            name = self.get_argument("name", None)
            if not name:
                self.set_status(400)
                self.finish(json.dumps({"error": "Configuration 'name' required as query parameter"}))
                return

            service = get_database_config_service()
            success = service.remove_config(db_type, name)

            if success:
                self.finish(json.dumps({
                    "success": True,
                    "message": f"Deleted {db_type} configuration: {name}"
                }))
            else:
                self.set_status(404)
                self.finish(json.dumps({"error": f"Configuration '{name}' not found"}))
        except Exception as e:
            self.set_status(500)
            self.finish(json.dumps({"error": str(e)}))


class DatabaseDefaultsHandler(APIHandler):
    """Handler for database defaults."""

    @tornado.web.authenticated
    def get(self):
        """Get defaults."""
        try:
            service = get_database_config_service()
            defaults = service.get_defaults()
            self.finish(json.dumps({"defaults": defaults}))
        except Exception as e:
            self.set_status(500)
            self.finish(json.dumps({"error": str(e)}))

    @tornado.web.authenticated
    def post(self):
        """Set defaults."""
        try:
            body = json.loads(self.request.body.decode('utf-8'))
            service = get_database_config_service()
            success = service.set_defaults(body)

            if success:
                self.finish(json.dumps({
                    "success": True,
                    "message": "Defaults updated"
                }))
            else:
                self.set_status(500)
                self.finish(json.dumps({"error": "Failed to set defaults"}))
        except json.JSONDecodeError as e:
            self.set_status(400)
            self.finish(json.dumps({"error": f"Invalid JSON: {str(e)}"}))
        except Exception as e:
            self.set_status(500)
            self.finish(json.dumps({"error": str(e)}))


class SignalPilotHomeInfoHandler(APIHandler):
    """Handler for getting SignalPilotHome directory info."""

    @tornado.web.authenticated
    def get(self):
        """Get SignalPilotHome information."""
        try:
            from .signalpilot_home import get_signalpilot_home
            home_manager = get_signalpilot_home()
            info = home_manager.get_info()
            self.finish(json.dumps(info))
        except Exception as e:
            self.set_status(500)
            self.finish(json.dumps({"error": str(e)}))
