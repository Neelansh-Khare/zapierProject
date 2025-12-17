"""
Manages the app registry JSON file.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from core.models import App


class RegistryManager:
    """Manages the universe app registry."""

    def __init__(self, registry_path: Optional[Path] = None):
        if registry_path is None:
            registry_path = Path(__file__).parent.parent / "app_registry.json"
        self.registry_path = registry_path
        self._ensure_registry_exists()

    def _ensure_registry_exists(self):
        """Ensure registry file exists with proper structure."""
        if not self.registry_path.exists():
            self._create_empty_registry()

    def _create_empty_registry(self):
        """Create an empty registry file."""
        registry = {
            "version": "1.0.0",
            "apps": [],
            "generated_at": None,
            "universe_config": None,
        }
        self._write_registry(registry)

    def add_app(self, app: App, app_path: Path):
        """Add an app to the registry."""
        registry = self.load_registry()
        
        app_entry = {
            "name": app.metadata.name,
            "category": app.metadata.category.value,
            "description": app.metadata.description,
            "action_count": len(app.actions),
            "path": str(app_path.relative_to(self.registry_path.parent.parent)),
            "version": app.version,
        }

        # Check if app already exists
        existing_index = next(
            (i for i, a in enumerate(registry["apps"]) if a["name"] == app.metadata.name),
            None,
        )

        if existing_index is not None:
            registry["apps"][existing_index] = app_entry
        else:
            registry["apps"].append(app_entry)

        registry["generated_at"] = datetime.utcnow().isoformat()
        self._write_registry(registry)

    def load_registry(self) -> Dict[str, Any]:
        """Load the registry from disk."""
        with open(self.registry_path, "r") as f:
            return json.load(f)

    def _write_registry(self, registry: Dict[str, Any]):
        """Write registry to disk."""
        with open(self.registry_path, "w") as f:
            json.dump(registry, f, indent=2)

    def get_apps(self) -> List[Dict[str, Any]]:
        """Get list of all apps in registry."""
        registry = self.load_registry()
        return registry.get("apps", [])

    def update_universe_config(self, config: Dict[str, Any]):
        """Update the universe config in the registry."""
        registry = self.load_registry()
        registry["universe_config"] = config
        self._write_registry(registry)

