"""
Script to create example apps from PRD.
Creates hand-crafted example apps matching the PRD's example_apps list.
"""

import json
from pathlib import Path

from core.models import AppCategory, SchemaComplexity, ErrorProfile, LatencyProfile
from tools.schema_generator.app_generator import AppGenerator
from universe.generator.registry_manager import RegistryManager


def create_example_apps():
    """Create the example apps from PRD."""
    generator = AppGenerator()
    registry_manager = RegistryManager()
    apps_dir = Path(__file__).parent.parent / "apps"
    apps_dir.mkdir(exist_ok=True)

    # Example apps from PRD
    example_apps = [
        {
            "name": "MailoMailer",
            "category": AppCategory.EMAIL,
            "action_count": 4,
            "complexity": SchemaComplexity.MEDIUM,
        },
        {
            "name": "TaskPad",
            "category": AppCategory.PRODUCTIVITY,
            "action_count": 5,
            "complexity": SchemaComplexity.MEDIUM,
        },
        {
            "name": "SheetForge",
            "category": AppCategory.STORAGE,
            "action_count": 4,
            "complexity": SchemaComplexity.HIGH,
        },
        {
            "name": "SalesPulseCRM",
            "category": AppCategory.CRM,
            "action_count": 5,
            "complexity": SchemaComplexity.HIGH,
        },
        {
            "name": "Slackette Messaging",
            "category": AppCategory.MESSAGING,
            "action_count": 4,
            "complexity": SchemaComplexity.MEDIUM,
        },
        {
            "name": "AutoBooker Calendar",
            "category": AppCategory.CALENDAR,
            "action_count": 5,
            "complexity": SchemaComplexity.MEDIUM,
        },
        {
            "name": "DriveHive Storage",
            "category": AppCategory.STORAGE,
            "action_count": 4,
            "complexity": SchemaComplexity.MEDIUM,
        },
    ]

    created_apps = []

    for app_config in example_apps:
        app = generator.generate_app(
            name=app_config["name"],
            category=app_config["category"],
            action_count=app_config["action_count"],
            schema_complexity=app_config["complexity"],
            error_profile=ErrorProfile.LOW,
            latency_profile=LatencyProfile.NORMAL,
        )

        # Save app to its directory
        app_dir = apps_dir / app_config["name"].lower().replace(" ", "_")
        app_dir.mkdir(exist_ok=True)

        app_file = app_dir / "definition.json"
        with open(app_file, "w") as f:
            json.dump(app.to_dict(), f, indent=2)

        # Register app in the universe registry
        registry_manager.add_app(app, app_dir)

        created_apps.append(app_config["name"])
        print(f"Created app: {app_config['name']} at {app_file}")

    print(f"\nCreated {len(created_apps)} example apps:")
    for name in created_apps:
        print(f"  - {name}")

    return created_apps


if __name__ == "__main__":
    create_example_apps()

