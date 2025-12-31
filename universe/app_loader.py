"""
Loads app definitions from the file system based on the app registry.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, List

from core.models import App
from universe.generator.registry_manager import RegistryManager


class AppLoader:
    """
    Loads app definitions from JSON files into App models.
    """

    def __init__(self, base_dir: Optional[Path] = None):
        if base_dir is None:
            self.base_dir = Path(__file__).parent.parent
        else:
            self.base_dir = base_dir
        
        self.registry_manager = RegistryManager(self.base_dir / "universe" / "app_registry.json")
        self._app_cache: Dict[str, App] = {}

    def load_app(self, app_name: str) -> Optional[App]:
        """
        Load a single app definition by name.
        """
        if app_name in self._app_cache:
            return self._app_cache[app_name]

        apps_in_registry = self.registry_manager.get_apps()
        app_info = next((app for app in apps_in_registry if app.get("metadata", {}).get("name") == app_name), None)

        if not app_info:
            return None

        # Determine path - registry doesn't store path directly, construct it
        app_def_path = self.base_dir / "apps" / app_name.lower().replace(" ", "_") / "definition.json"
        
        if not app_def_path.exists():
            print(f"Warning: App definition file not found for {app_name} at {app_def_path}")
            return None

        with open(app_def_path, "r") as f:
            app_data = json.load(f)
            app = App(**app_data)
            self._app_cache[app_name] = app
            return app

    def get_all_apps(self) -> List[App]:
        """
        Load all apps listed in the registry.
        """
        all_apps = []
        apps_in_registry = self.registry_manager.get_apps()
        for app_info in apps_in_registry:
            name = app_info.get("metadata", {}).get("name")
            if name:
                app = self.load_app(name)
                if app:
                    all_apps.append(app)
        return all_apps

# Global AppLoader instance
_app_loader = None

def get_app_loader() -> AppLoader:
    """
    Get the global AppLoader instance.
    """
    global _app_loader
    if _app_loader is None:
        _app_loader = AppLoader()
    return _app_loader
