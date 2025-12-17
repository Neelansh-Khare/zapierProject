"""
App generator that creates complete app definitions from templates.
"""

import random
from typing import Dict, Any, List, Optional, Tuple
from faker import Faker

from core.models import (
    App,
    AppMetadata,
    Action,
    RateLimitProfile,
    StateDefinition,
    AppCategory,
    SchemaComplexity,
    ErrorType,
    ErrorDistribution,
    ErrorProfile,
    LatencyProfile,
)
from tools.schema_generator.schema_builder import SchemaBuilder


class AppGenerator:
    """Generates synthetic apps from templates and configuration."""

    def __init__(self):
        self.faker = Faker()
        self.schema_builder = SchemaBuilder()

    def generate_app(
        self,
        name: str,
        category: AppCategory,
        action_count: int = 3,
        schema_complexity: SchemaComplexity = SchemaComplexity.MEDIUM,
        rate_limits: Optional[RateLimitProfile] = None,
        error_profile: ErrorProfile = ErrorProfile.LOW,
        latency_profile: LatencyProfile = LatencyProfile.NORMAL,
        default_state: Optional[Dict[str, Any]] = None,
    ) -> App:
        """
        Generate a complete app definition.
        
        Args:
            name: App name
            category: App category
            action_count: Number of actions to generate
            schema_complexity: Complexity level for schemas
            rate_limits: Rate limit profile (defaults to category-based)
            error_profile: Error profile level
            latency_profile: Latency profile level
            default_state: Initial state structure
            
        Returns:
            Complete App definition
        """
        # Generate metadata
        metadata = AppMetadata(
            name=name,
            category=category,
            description=self._generate_description(name, category),
        )

        # Generate rate limits if not provided
        if rate_limits is None:
            rate_limits = self._generate_rate_limits(category)

        # Generate actions
        actions = self._generate_actions(
            category=category,
            count=action_count,
            complexity=schema_complexity,
            error_profile=error_profile,
            latency_profile=latency_profile,
        )

        # Generate state definition
        state_definition = self._generate_state_definition(
            category=category,
            default_state=default_state,
        )

        return App(
            metadata=metadata,
            actions=actions,
            rate_limits=rate_limits,
            state_definition=state_definition,
        )

    def _generate_description(self, name: str, category: AppCategory) -> str:
        """Generate a realistic app description."""
        descriptions = {
            AppCategory.EMAIL: f"{name} is a powerful email automation platform for managing communications.",
            AppCategory.STORAGE: f"{name} provides cloud storage and file management capabilities.",
            AppCategory.PRODUCTIVITY: f"{name} helps teams manage tasks and boost productivity.",
            AppCategory.CRM: f"{name} is a customer relationship management system for sales teams.",
            AppCategory.FINANCE: f"{name} handles financial transactions and accounting workflows.",
            AppCategory.DEVELOPER_TOOLS: f"{name} offers developer tools and API integrations.",
            AppCategory.MESSAGING: f"{name} enables team messaging and collaboration.",
            AppCategory.CALENDAR: f"{name} manages calendars and scheduling.",
            AppCategory.OPERATIONS: f"{name} automates operational workflows.",
            AppCategory.FILE_PROCESSING: f"{name} processes and transforms files.",
        }
        return descriptions.get(category, f"{name} is a versatile automation platform.")

    def _generate_rate_limits(self, category: AppCategory) -> RateLimitProfile:
        """Generate rate limits based on category."""
        # Different categories have different typical rate limits
        limits = {
            AppCategory.EMAIL: (60, 10),
            AppCategory.STORAGE: (100, 20),
            AppCategory.PRODUCTIVITY: (120, 15),
            AppCategory.CRM: (200, 30),
            AppCategory.FINANCE: (30, 5),
            AppCategory.DEVELOPER_TOOLS: (300, 50),
            AppCategory.MESSAGING: (180, 25),
            AppCategory.CALENDAR: (100, 15),
            AppCategory.OPERATIONS: (150, 20),
            AppCategory.FILE_PROCESSING: (80, 12),
        }
        requests_per_min, burst = limits.get(category, (60, 10))
        return RateLimitProfile(requests_per_min=requests_per_min, burst_limit=burst)

    def _generate_actions(
        self,
        category: AppCategory,
        count: int,
        complexity: SchemaComplexity,
        error_profile: ErrorProfile,
        latency_profile: LatencyProfile,
    ) -> List[Action]:
        """Generate actions for an app based on category."""
        action_templates = self._get_action_templates(category)
        actions = []

        # Select actions from templates
        selected_actions = random.sample(
            action_templates, min(count, len(action_templates))
        )

        for action_name in selected_actions:
            # Generate schemas
            inputs_schema = self.schema_builder.generate_input_schema(
                action_name, category, complexity
            )
            outputs_schema = self.schema_builder.generate_output_schema(
                action_name, category, complexity
            )

            # Determine side effects
            side_effects = self._determine_side_effects(action_name, category)

            # Determine possible errors
            errors = self._determine_errors(category, error_profile)

            # Generate error distributions
            error_distributions = self._generate_error_distributions(
                errors, error_profile
            )

            # Determine latency range
            latency_range = self._get_latency_range(latency_profile)

            action = Action(
                name=action_name,
                inputs_schema=inputs_schema,
                outputs_schema=outputs_schema,
                side_effects=side_effects,
                errors=errors,
                error_distributions=error_distributions,
                latency_range_ms=latency_range,
            )
            actions.append(action)

        return actions

    def _get_action_templates(self, category: AppCategory) -> List[str]:
        """Get action name templates for a category."""
        templates = {
            AppCategory.EMAIL: [
                "send_email",
                "get_email",
                "list_emails",
                "delete_email",
                "mark_as_read",
            ],
            AppCategory.STORAGE: [
                "upload_file",
                "download_file",
                "list_files",
                "delete_file",
                "create_folder",
            ],
            AppCategory.PRODUCTIVITY: [
                "create_task",
                "update_task",
                "get_task",
                "list_tasks",
                "complete_task",
            ],
            AppCategory.CRM: [
                "create_contact",
                "update_contact",
                "get_contact",
                "list_contacts",
                "delete_contact",
            ],
            AppCategory.FINANCE: [
                "create_transaction",
                "get_balance",
                "list_transactions",
                "create_invoice",
            ],
            AppCategory.DEVELOPER_TOOLS: [
                "trigger_webhook",
                "get_logs",
                "deploy_service",
                "check_status",
            ],
            AppCategory.MESSAGING: [
                "send_message",
                "get_message",
                "list_messages",
                "create_channel",
            ],
            AppCategory.CALENDAR: [
                "create_event",
                "update_event",
                "get_event",
                "list_events",
                "delete_event",
            ],
            AppCategory.OPERATIONS: [
                "create_workflow",
                "trigger_workflow",
                "get_status",
                "list_workflows",
            ],
            AppCategory.FILE_PROCESSING: [
                "process_file",
                "convert_format",
                "extract_data",
                "merge_files",
            ],
        }
        return templates.get(category, ["create_resource", "get_resource", "update_resource"])

    def _determine_side_effects(self, action_name: str, category: AppCategory) -> List[str]:
        """Determine what side effects an action has."""
        side_effects = []
        if "create" in action_name or "send" in action_name:
            side_effects.append("creates_resource")
        if "update" in action_name or "modify" in action_name:
            side_effects.append("updates_resource")
        if "delete" in action_name or "remove" in action_name:
            side_effects.append("deletes_resource")
        return side_effects

    def _determine_errors(
        self, category: AppCategory, error_profile: ErrorProfile
    ) -> List[ErrorType]:
        """Determine possible errors for actions in this category."""
        base_errors = [ErrorType.RATE_LIMIT, ErrorType.SCHEMA_ERROR]
        
        if error_profile == ErrorProfile.NONE:
            return []
        elif error_profile == ErrorProfile.LOW:
            return base_errors
        elif error_profile == ErrorProfile.MEDIUM:
            return base_errors + [ErrorType.AUTH_ERROR, ErrorType.NETWORK_UNREACHABLE]
        else:  # HIGH
            return [
                ErrorType.RATE_LIMIT,
                ErrorType.AUTH_EXPIRED,
                ErrorType.NETWORK_UNREACHABLE,
                ErrorType.SCHEMA_ERROR,
                ErrorType.PARTIAL_FAILURE,
                ErrorType.DATA_INCONSISTENCY,
            ]

    def _generate_error_distributions(
        self, errors: List[ErrorType], error_profile: ErrorProfile
    ) -> List[ErrorDistribution]:
        """Generate error probability distributions."""
        if error_profile == ErrorProfile.NONE:
            return []

        distributions = []
        probabilities = {
            ErrorProfile.LOW: 0.01,
            ErrorProfile.MEDIUM: 0.05,
            ErrorProfile.HIGH: 0.15,
        }
        base_prob = probabilities.get(error_profile, 0.01)

        for error_type in errors:
            # Different error types have different base probabilities
            prob = base_prob
            if error_type == ErrorType.RATE_LIMIT:
                prob = base_prob * 0.5
            elif error_type == ErrorType.AUTH_EXPIRED:
                prob = base_prob * 0.3
            elif error_type == ErrorType.NETWORK_UNREACHABLE:
                prob = base_prob * 0.2

            distributions.append(
                ErrorDistribution(error_type=error_type, probability=prob, enabled=True)
            )

        return distributions

    def _get_latency_range(self, latency_profile: LatencyProfile) -> Tuple[int, int]:
        """Get latency range based on profile."""
        ranges = {
            LatencyProfile.FAST: (20, 100),
            LatencyProfile.NORMAL: (50, 400),
            LatencyProfile.SLOW: (200, 2000),
        }
        return ranges.get(latency_profile, (50, 400))

    def _generate_state_definition(
        self,
        category: AppCategory,
        default_state: Optional[Dict[str, Any]] = None,
    ) -> StateDefinition:
        """Generate state definition for an app."""
        if default_state is not None:
            return StateDefinition(initial_state=default_state)

        # Category-specific default states
        default_states = {
            AppCategory.EMAIL: {"emails": [], "folders": []},
            AppCategory.STORAGE: {"files": [], "folders": []},
            AppCategory.PRODUCTIVITY: {"tasks": []},
            AppCategory.CRM: {"contacts": [], "companies": []},
            AppCategory.FINANCE: {"transactions": [], "balance": 0.0},
            AppCategory.MESSAGING: {"messages": [], "channels": []},
            AppCategory.CALENDAR: {"events": []},
        }

        initial_state = default_states.get(category, {"resources": []})
        state_schema = {
            "type": "object",
            "properties": {
                k: {"type": type(v).__name__} for k, v in initial_state.items()
            },
        }

        return StateDefinition(initial_state=initial_state, state_schema=state_schema)

