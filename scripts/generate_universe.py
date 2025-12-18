"""Script to generate a universe of synthetic apps."""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from universe.config import UniverseConfig
from universe.generator.randomizer import UniverseRandomizer
from tools.universe_scaler.scaler import UniverseScaler
from core.models import AppCategory


def main():
    """Generate a universe of apps."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate a universe of synthetic apps")
    parser.add_argument(
        "--num-apps",
        type=int,
        default=200,
        help="Number of apps to generate (default: 200)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="universe/app_registry.json",
        help="Output file path (default: universe/app_registry.json)"
    )
    parser.add_argument(
        "--chaos-level",
        type=float,
        default=1.0,
        help="Chaos level (0.0-2.0, default: 1.0)"
    )
    parser.add_argument(
        "--categories",
        nargs="+",
        default=None,
        help="Categories to include (default: all). Options: email, storage, productivity, crm, finance, developer_tools, messaging, calendar, operations, file_processing"
    )
    parser.add_argument(
        "--apps-dir",
        type=str,
        default="apps",
        help="Directory to save generated apps (default: apps)"
    )
    
    args = parser.parse_args()
    
    # Convert category strings to AppCategory enums if provided
    categories = None
    if args.categories:
        category_map = {
            "email": AppCategory.EMAIL,
            "storage": AppCategory.STORAGE,
            "productivity": AppCategory.PRODUCTIVITY,
            "crm": AppCategory.CRM,
            "finance": AppCategory.FINANCE,
            "developer_tools": AppCategory.DEVELOPER_TOOLS,
            "messaging": AppCategory.MESSAGING,
            "calendar": AppCategory.CALENDAR,
            "operations": AppCategory.OPERATIONS,
            "file_processing": AppCategory.FILE_PROCESSING,
        }
        categories = [category_map[cat.lower()] for cat in args.categories if cat.lower() in category_map]
    
    # Create config
    config = UniverseConfig(
        num_apps=args.num_apps,
        chaos_level=args.chaos_level
    )
    
    if categories:
        config.categories_enabled = categories
    
    print(f"Generating universe with {args.num_apps} apps...")
    print(f"Categories: {[cat.value for cat in config.categories_enabled]}")
    print(f"Chaos level: {args.chaos_level}")
    
    # Generate universe using scaler
    scaler = UniverseScaler(config)
    apps_dir = Path(__file__).parent.parent / args.apps_dir
    
    # Generate and save apps
    generated_apps = scaler.add_apps_to_universe(
        count=args.num_apps,
        categories=config.categories_enabled,
        apps_dir=apps_dir
    )
    
    print(f"\n✓ Generated {len(generated_apps)} apps")
    print(f"✓ Apps saved to {apps_dir}")
    
    # Also generate registry with all apps
    print("\nGenerating app registry...")
    scaler.generate_app_registry_json(args.output)
    print(f"✓ App registry generated at {args.output}")


if __name__ == "__main__":
    main()

