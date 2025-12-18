"""Universe randomizer for generating diverse synthetic universes."""
import random
from typing import List, Dict, Any, Optional

from universe.config import UniverseConfig
from tools.schema_generator.app_generator import AppGenerator
from core.models import AppCategory, SchemaComplexity, ErrorProfile, LatencyProfile


class UniverseRandomizer:
    """Generates random but realistic universes."""
    
    def __init__(self, config: Optional[UniverseConfig] = None):
        self.config = config or UniverseConfig.default()
        self.generator = AppGenerator()
    
    def generate_universe(self) -> Dict[str, Any]:
        """Generate a random universe of apps."""
        # Distribute apps across categories
        category_distribution = self._distribute_apps()
        
        apps = []
        for category, count in category_distribution.items():
            category_apps = self._generate_apps_for_category(category, count)
            apps.extend(category_apps)
        
        return {
            "config": self.config.model_dump(),
            "apps": apps,
            "total_apps": len(apps)
        }
    
    def _generate_apps_for_category(self, category: AppCategory, count: int) -> List[Dict[str, Any]]:
        """Generate apps for a specific category."""
        apps = []
        for _ in range(count):
            # Generate random app name
            app_name = self._generate_app_name(category)
            
            # Generate app with random complexity
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
            apps.append(app.to_dict())
        
        return apps
    
    def _generate_app_name(self, category: AppCategory) -> str:
        """Generate a realistic app name for a category."""
        prefixes = {
            AppCategory.EMAIL: ["Mail", "Send", "Notify", "Inbox"],
            AppCategory.STORAGE: ["Drive", "Box", "Store", "Vault"],
            AppCategory.PRODUCTIVITY: ["Task", "Note", "Plan", "Do"],
            AppCategory.CRM: ["Sales", "Client", "Contact", "Pulse"],
            AppCategory.FINANCE: ["Pay", "Bill", "Invoice", "Money"],
            AppCategory.DEVELOPER_TOOLS: ["Code", "Dev", "Build", "Deploy"],
            AppCategory.MESSAGING: ["Chat", "Message", "Slack", "Talk"],
            AppCategory.CALENDAR: ["Cal", "Schedule", "Event", "Meet"],
            AppCategory.OPERATIONS: ["Ops", "Manage", "Control", "Flow"],
            AppCategory.FILE_PROCESSING: ["File", "Doc", "Process", "Convert"],
        }
        suffixes = ["Hub", "Pro", "Plus", "Lite", "Cloud", "API", "Forge", "Pad"]
        
        prefix_list = prefixes.get(category, ["App"])
        prefix = random.choice(prefix_list)
        suffix = random.choice(suffixes)
        return f"{prefix}{suffix}"
    
    def _distribute_apps(self) -> Dict[AppCategory, int]:
        """Distribute apps across categories."""
        total_apps = self.config.num_apps
        categories = self.config.categories_enabled
        
        # Use weighted random distribution
        distribution = {cat: 0 for cat in categories}
        
        # Assign minimum 1 app per category
        for cat in categories:
            distribution[cat] = 1
        
        remaining = total_apps - len(categories)
        
        # Distribute remaining apps randomly
        for _ in range(remaining):
            category = random.choice(categories)
            distribution[category] += 1
        
        return distribution

