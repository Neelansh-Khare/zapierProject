"""
JSON Schema generator for app actions.
Generates realistic schemas based on category, complexity, and action type.
"""

import random
from typing import Dict, Any, List, Literal
from faker import Faker

from core.models import AppCategory, SchemaComplexity, Action, ErrorType

fake = Faker()


class SchemaBuilder:
    """Builds JSON schemas for action inputs and outputs."""

    def __init__(self):
        self.faker = Faker()

    def generate_input_schema(
        self,
        action_name: str,
        category: AppCategory,
        complexity: SchemaComplexity = SchemaComplexity.MEDIUM,
    ) -> Dict[str, Any]:
        """
        Generate input schema for an action based on its name and category.
        
        Args:
            action_name: Name of the action (e.g., 'send_email', 'create_task')
            category: App category
            complexity: Schema complexity level
            
        Returns:
            JSON Schema dict for inputs
        """
        # Base schema structure
        schema = {
            "type": "object",
            "properties": {},
            "required": [],
        }

        # Generate fields based on action name patterns and category
        if "send" in action_name.lower() or "create" in action_name.lower():
            schema = self._generate_create_schema(action_name, category, complexity)
        elif "get" in action_name.lower() or "fetch" in action_name.lower():
            schema = self._generate_fetch_schema(action_name, category, complexity)
        elif "update" in action_name.lower() or "modify" in action_name.lower():
            schema = self._generate_update_schema(action_name, category, complexity)
        elif "delete" in action_name.lower() or "remove" in action_name.lower():
            schema = self._generate_delete_schema(action_name, category, complexity)
        else:
            # Generic schema
            schema = self._generate_generic_schema(action_name, category, complexity)

        return schema

    def generate_output_schema(
        self,
        action_name: str,
        category: AppCategory,
        complexity: SchemaComplexity = SchemaComplexity.MEDIUM,
    ) -> Dict[str, Any]:
        """
        Generate output schema for an action.
        
        Args:
            action_name: Name of the action
            category: App category
            complexity: Schema complexity level
            
        Returns:
            JSON Schema dict for outputs
        """
        schema = {
            "type": "object",
            "properties": {
                "id": {"type": "string", "description": "Resource ID"},
                "status": {"type": "string", "description": "Operation status"},
                "created_at": {"type": "string", "format": "date-time", "description": "Creation timestamp"},
            },
            "required": ["id", "status"],
        }

        # Add category-specific fields
        if category == AppCategory.EMAIL:
            schema["properties"]["message_id"] = {"type": "string"}
            schema["properties"]["recipient"] = {"type": "string"}
        elif category == AppCategory.CRM:
            schema["properties"]["contact_id"] = {"type": "string"}
            schema["properties"]["company"] = {"type": "string"}
        elif category == AppCategory.STORAGE:
            schema["properties"]["file_id"] = {"type": "string"}
            schema["properties"]["file_url"] = {"type": "string"}
        elif category == AppCategory.PRODUCTIVITY:
            schema["properties"]["task_id"] = {"type": "string"}
            schema["properties"]["priority"] = {"type": "string"}

        # Add complexity-based fields
        if complexity == SchemaComplexity.HIGH:
            schema["properties"]["metadata"] = {
                "type": "object",
                "properties": {
                    "version": {"type": "string"},
                    "tags": {"type": "array", "items": {"type": "string"}},
                },
            }
            schema["properties"]["related_resources"] = {
                "type": "array",
                "items": {"type": "object"},
            }

        return schema

    def _generate_create_schema(
        self, action_name: str, category: AppCategory, complexity: SchemaComplexity
    ) -> Dict[str, Any]:
        """Generate schema for create/send actions."""
        schema = {"type": "object", "properties": {}, "required": []}

        if category == AppCategory.EMAIL:
            schema["properties"] = {
                "to": {"type": "string", "format": "email", "description": "Recipient email"},
                "subject": {"type": "string", "description": "Email subject"},
                "body": {"type": "string", "description": "Email body"},
            }
            schema["required"] = ["to", "subject"]
            if complexity != SchemaComplexity.LOW:
                schema["properties"]["cc"] = {"type": "array", "items": {"type": "string", "format": "email"}}
                schema["properties"]["attachments"] = {"type": "array", "items": {"type": "string"}}

        elif category == AppCategory.CRM:
            schema["properties"] = {
                "name": {"type": "string", "description": "Contact name"},
                "email": {"type": "string", "format": "email", "description": "Contact email"},
            }
            schema["required"] = ["name", "email"]
            if complexity != SchemaComplexity.LOW:
                schema["properties"]["phone"] = {"type": "string"}
                schema["properties"]["company"] = {"type": "string"}
                if complexity == SchemaComplexity.HIGH:
                    schema["properties"]["custom_fields"] = {"type": "object"}

        elif category == AppCategory.STORAGE:
            schema["properties"] = {
                "filename": {"type": "string", "description": "File name"},
                "content": {"type": "string", "description": "File content (base64 or text)"},
            }
            schema["required"] = ["filename"]
            if complexity != SchemaComplexity.LOW:
                schema["properties"]["folder"] = {"type": "string"}
                schema["properties"]["metadata"] = {"type": "object"}

        elif category == AppCategory.PRODUCTIVITY:
            schema["properties"] = {
                "title": {"type": "string", "description": "Task title"},
                "description": {"type": "string", "description": "Task description"},
            }
            schema["required"] = ["title"]
            if complexity != SchemaComplexity.LOW:
                schema["properties"]["due_date"] = {"type": "string", "format": "date-time"}
                schema["properties"]["priority"] = {"type": "string", "enum": ["low", "medium", "high"]}

        elif category == AppCategory.MESSAGING:
            schema["properties"] = {
                "channel": {"type": "string", "description": "Channel ID"},
                "message": {"type": "string", "description": "Message text"},
            }
            schema["required"] = ["channel", "message"]

        elif category == AppCategory.CALENDAR:
            schema["properties"] = {
                "title": {"type": "string", "description": "Event title"},
                "start_time": {"type": "string", "format": "date-time", "description": "Event start time"},
            }
            schema["required"] = ["title", "start_time"]
            if complexity != SchemaComplexity.LOW:
                schema["properties"]["end_time"] = {"type": "string", "format": "date-time"}
                schema["properties"]["attendees"] = {"type": "array", "items": {"type": "string", "format": "email"}}

        else:
            # Generic create schema
            schema["properties"] = {
                "name": {"type": "string", "description": "Resource name"},
                "data": {"type": "object", "description": "Resource data"},
            }
            schema["required"] = ["name"]

        return schema

    def _generate_fetch_schema(
        self, action_name: str, category: AppCategory, complexity: SchemaComplexity
    ) -> Dict[str, Any]:
        """Generate schema for fetch/get actions."""
        schema = {
            "type": "object",
            "properties": {
                "id": {"type": "string", "description": "Resource ID"},
            },
            "required": ["id"],
        }

        if complexity != SchemaComplexity.LOW:
            schema["properties"]["include_metadata"] = {"type": "boolean", "default": False}
            if complexity == SchemaComplexity.HIGH:
                schema["properties"]["fields"] = {"type": "array", "items": {"type": "string"}}

        return schema

    def _generate_update_schema(
        self, action_name: str, category: AppCategory, complexity: SchemaComplexity
    ) -> Dict[str, Any]:
        """Generate schema for update actions."""
        schema = {
            "type": "object",
            "properties": {
                "id": {"type": "string", "description": "Resource ID"},
            },
            "required": ["id"],
        }

        # Add update fields based on category
        if category == AppCategory.EMAIL:
            schema["properties"]["subject"] = {"type": "string"}
            schema["properties"]["body"] = {"type": "string"}
        elif category == AppCategory.CRM:
            schema["properties"]["name"] = {"type": "string"}
            schema["properties"]["email"] = {"type": "string"}
        elif category == AppCategory.PRODUCTIVITY:
            schema["properties"]["title"] = {"type": "string"}
            schema["properties"]["status"] = {"type": "string", "enum": ["pending", "in_progress", "completed"]}

        return schema

    def _generate_delete_schema(
        self, action_name: str, category: AppCategory, complexity: SchemaComplexity
    ) -> Dict[str, Any]:
        """Generate schema for delete actions."""
        return {
            "type": "object",
            "properties": {
                "id": {"type": "string", "description": "Resource ID"},
            },
            "required": ["id"],
        }

    def _generate_generic_schema(
        self, action_name: str, category: AppCategory, complexity: SchemaComplexity
    ) -> Dict[str, Any]:
        """Generate generic schema for unknown action patterns."""
        return {
            "type": "object",
            "properties": {
                "data": {"type": "object", "description": "Action data"},
            },
            "required": [],
        }

