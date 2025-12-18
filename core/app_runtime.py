"""
App Runtime Engine.
Loads an app definition and provides methods to execute its actions.
"""

import asyncio
import random
import time
import jsonschema
from typing import Dict, Any, Optional

from core.models import App, Action
from core.state.engine import get_state_engine
from core.errors.simulator import get_error_simulator, ErrorSimulator


class AppRuntime:
    """
    A runtime environment for executing actions of a single synthetic app.
    """

    def __init__(self, app: App, error_simulator: Optional[ErrorSimulator] = None):
        self.app = app
        self.state_engine = get_state_engine()
        self.error_simulator = error_simulator or get_error_simulator()

        # Configure error simulator for this app
        self.error_simulator.configure_rate_limit(
            self.app.metadata.name,
            self.app.rate_limits.requests_per_min,
            self.app.rate_limits.burst_limit,
        )
        self.error_simulator.set_auth_state(self.app.metadata.name, True)
        self.error_simulator.set_network_state(self.app.metadata.name, True)

    async def execute_action(self, action_name: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an action with error simulation and latency.
        """
        action = self.app.get_action(action_name)
        if not action:
            return {
                "success": False,
                "error": {
                    "type": "action_not_found",
                    "message": f"Action '{action_name}' not found in app '{self.app.metadata.name}'",
                },
            }

        # Record request for rate limiting
        self.error_simulator.record_request(self.app.metadata.name)

        # Simulate latency
        latency_ms = random.randint(action.latency_range_ms[0], action.latency_range_ms[1])
        await asyncio.sleep(latency_ms / 1000.0)

        # Check for errors
        error = self.error_simulator.simulate_error(self.app.metadata.name, action_name)
        if error:
            return {"success": False, "error": error}

        # Validate inputs
        try:
            jsonschema.validate(inputs, action.inputs_schema)
        except jsonschema.ValidationError as e:
            return {
                "success": False,
                "error": {
                    "type": "schema_error",
                    "message": f"Invalid input schema: {e.message}",
                    "details": {"validation_error": str(e)},
                },
            }

        # Execute the action
        try:
            result = await self._execute_action_impl(action, inputs)

            # Validate outputs
            try:
                jsonschema.validate(result, action.outputs_schema)
            except jsonschema.ValidationError as e:
                print(f"Warning: Output validation failed for {action_name}: {e}")

            return {"success": True, "result": result, "latency_ms": latency_ms}
        except Exception as e:
            return {
                "success": False,
                "error": {
                    "type": "execution_error",
                    "message": f"Action execution failed: {str(e)}",
                    "details": {"exception": str(e)},
                },
            }

    async def _execute_action_impl(self, action: Action, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generic implementation of action logic based on action name patterns.
        This simulates CRUD operations on the state engine.
        """
        action_name = action.name
        app_name = self.app.metadata.name
        
        # Infer object type from action name (e.g., "create_contact" -> "contacts")
        # This is a heuristic and might need to be more robust.
        object_type = action_name.split("_")[-1] + "s"
        if "list" in action_name:
            object_type = action_name.split("_")[-1]

        if "create" in action_name or "add" in action_name or "send" in action_name:
            obj_id = self.state_engine.create_object(app_name, object_type, inputs)
            return {"id": obj_id, "status": "success", **inputs}

        elif "update" in action_name or "edit" in action_name:
            obj_id = inputs.pop("id", None)
            if not obj_id:
                raise ValueError("Missing 'id' for update operation")
            success = self.state_engine.update_object(app_name, object_type, obj_id, inputs)
            if not success:
                raise ValueError(f"Object {obj_id} not found")
            updated_obj = self.state_engine.read_object(app_name, object_type, obj_id)
            return updated_obj

        elif "delete" in action_name or "remove" in action_name:
            obj_id = inputs.get("id")
            if not obj_id:
                raise ValueError("Missing 'id' for delete operation")
            success = self.state_engine.delete_object(app_name, object_type, obj_id)
            if not success:
                raise ValueError(f"Object {obj_id} not found")
            return {"id": obj_id, "status": "deleted"}

        elif "get" in action_name or "fetch" in action_name:
            obj_id = inputs.get("id")
            if not obj_id:
                raise ValueError("Missing 'id' for get operation")
            obj = self.state_engine.read_object(app_name, object_type, obj_id)
            if not obj:
                raise ValueError(f"Object {obj_id} not found")
            return obj

        elif "list" in action_name:
            all_objects = self.state_engine.get_app_state(app_name).get(object_type, [])
            # Simple filtering for demonstration
            limit = inputs.get("limit", 50)
            return {"results": all_objects[:limit], "count": len(all_objects)}

        else:
            # Default behavior for unknown action patterns
            print(f"Warning: No specific implementation for action '{action_name}'. Returning inputs.")
            return {"status": "executed", "result": inputs}

