"""Universe scaler for managing universe size and complexity."""
import json
import random
from typing import Dict, List, Any, Optional
from pathlib import Path

from universe.config import UniverseConfig, load_config
from tools.schema_generator.app_generator import AppGenerator
from universe.generator.randomizer import UniverseRandomizer
from universe.app_loader import get_app_loader
from universe.generator.registry_manager import RegistryManager
from core.models import App, AppCategory, SchemaComplexity, ErrorProfile, LatencyProfile


class UniverseScaler:
    """Manages universe scaling and generation."""
    
    def __init__(self, config: Optional[UniverseConfig] = None):
        self.config = config or UniverseConfig.default()
        self.generator = AppGenerator()
        self.randomizer = UniverseRandomizer(self.config)
        self.app_loader = get_app_loader()
    
    def scale_universe(
        self,
        target_size: int,
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Scale universe to target size.
        
        Args:
            target_size: Target number of apps
            output_path: Optional path to save universe definition
            
        Returns:
            Universe definition dict
        """
        # Update config
        self.config.num_apps = target_size
        
        # Generate universe
        universe = self.randomizer.generate_universe()
        
        # Save if path provided
        if output_path:
            self.save_universe(universe, output_path)
        
        return universe
    
    def add_apps_to_universe(
        self,
        count: int,
        categories: Optional[List[AppCategory]] = None,
        apps_dir: Optional[Path] = None
    ) -> List[App]:
        """Add more apps to the universe."""
        if apps_dir is None:
            apps_dir = Path(__file__).parent.parent.parent / "apps"
        apps_dir.mkdir(exist_ok=True)
        
        if categories is None:
            categories = self.config.categories_enabled
        
        registry_manager = RegistryManager()
        new_apps = []
        
        for _ in range(count):
            category = categories[0] if len(categories) == 1 else random.choice(categories)
            
            # Generate random app name
            app_name = self.randomizer._generate_app_name(category)
            complexity = random.choice([
                SchemaComplexity.LOW,
                SchemaComplexity.MEDIUM,
                SchemaComplexity.HIGH
            ])
            
            app = self.generator.generate_app(
                name=app_name,
                category=category,
                action_count=random.randint(3, 8),
                schema_complexity=complexity,
                error_profile=ErrorProfile.LOW,
                latency_profile=LatencyProfile.NORMAL,
            )
            
            # Save app to its directory
            app_dir = apps_dir / app_name.lower().replace(" ", "_")
            app_dir.mkdir(exist_ok=True)
            
            app_file = app_dir / "definition.json"
            with open(app_file, "w") as f:
                json.dump(app.to_dict(), f, indent=2)
            
            # Register app in the universe registry
            registry_manager.add_app(app, app_dir)
            
            new_apps.append(app)
        
        return new_apps
    
    def save_universe(self, universe: Dict[str, Any], path: str) -> None:
        """Save universe definition to file."""
        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(universe, f, indent=2)
    
    def load_universe(self, path: str) -> Dict[str, Any]:
        """Load universe definition from file."""
        with open(path, 'r') as f:
            return json.load(f)
    
    def generate_app_registry_json(
        self,
        output_path: str = "universe/app_registry.json"
    ) -> None:
        """Generate app registry JSON file from loaded apps."""
        all_apps = self.app_loader.get_all_apps()
        apps_data = [app.to_dict() for app in all_apps]
        
        universe_def = {
            "version": "1.0.0",
            "total_apps": len(apps_data),
            "apps": apps_data,
            "config": self.config.model_dump()
        }
        
        self.save_universe(universe_def, output_path)
    
    def cleanup_state(self, app_names: Optional[List[str]] = None) -> None:
        """Clean up state for apps (episodic cleanup)."""
        from core.state.engine import get_state_engine
        
        state_engine = get_state_engine()
        
        if app_names:
            for app_name in app_names:
                state_engine.clear_app_state(app_name)
        else:
            # Clean up all app states
            all_apps = self.app_loader.get_all_apps()
            for app in all_apps:
                state_engine.clear_app_state(app.metadata.name)


def scale_universe_to_size(
    target_size: int,
    config: Optional[UniverseConfig] = None
) -> Dict[str, Any]:
    """Convenience function to scale universe."""
    scaler = UniverseScaler(config)
    return scaler.scale_universe(target_size)

