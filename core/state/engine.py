"""Global state and per-app state simulation engine."""
import json
import threading
import time
from typing import Dict, List, Any, Optional, Callable
from collections import defaultdict
from datetime import datetime
import uuid


class StateEngine:
    """Manages global and per-app state with CRUD operations and event propagation."""
    
    def __init__(self):
        self.global_state: Dict[str, Any] = {}
        self.app_states: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self.shared_objects: Dict[str, Any] = {}
        self.event_listeners: Dict[str, List[Callable]] = defaultdict(list)
        self.lock = threading.RLock()
        self.synthetic_data_generator = SyntheticDataGenerator()
        
    def get_app_state(self, app_name: str) -> Dict[str, Any]:
        """Get state for a specific app."""
        with self.lock:
            return self.app_states[app_name].copy()
    
    def set_app_state(self, app_name: str, key: str, value: Any) -> None:
        """Set a value in app state."""
        with self.lock:
            if app_name not in self.app_states:
                self.app_states[app_name] = {}
            self.app_states[app_name][key] = value
            self._propagate_event(app_name, "state_change", {"key": key, "value": value})
    
    def update_app_state(self, app_name: str, updates: Dict[str, Any]) -> None:
        """Batch update app state."""
        with self.lock:
            if app_name not in self.app_states:
                self.app_states[app_name] = {}
            self.app_states[app_name].update(updates)
            self._propagate_event(app_name, "state_update", updates)
    
    def create_object(self, app_name: str, object_type: str, data: Dict[str, Any]) -> str:
        """Create a new object and return its ID."""
        with self.lock:
            if app_name not in self.app_states:
                self.app_states[app_name] = {}
            if object_type not in self.app_states[app_name]:
                self.app_states[app_name][object_type] = []
            
            obj_id = str(uuid.uuid4())
            obj = {
                "id": obj_id,
                "created_at": datetime.now().isoformat(),
                **data
            }
            self.app_states[app_name][object_type].append(obj)
            self._propagate_event(app_name, "create", {"type": object_type, "id": obj_id})
            return obj_id
    
    def read_object(self, app_name: str, object_type: str, obj_id: str) -> Optional[Dict[str, Any]]:
        """Read an object by ID."""
        with self.lock:
            if app_name not in self.app_states:
                return None
            objects = self.app_states[app_name].get(object_type, [])
            for obj in objects:
                if obj.get("id") == obj_id:
                    return obj.copy()
            return None
    
    def update_object(self, app_name: str, object_type: str, obj_id: str, updates: Dict[str, Any]) -> bool:
        """Update an object by ID."""
        with self.lock:
            if app_name not in self.app_states:
                return False
            objects = self.app_states[app_name].get(object_type, [])
            for obj in objects:
                if obj.get("id") == obj_id:
                    obj.update(updates)
                    obj["updated_at"] = datetime.now().isoformat()
                    self._propagate_event(app_name, "update", {"type": object_type, "id": obj_id})
                    return True
            return False
    
    def delete_object(self, app_name: str, object_type: str, obj_id: str) -> bool:
        """Delete an object by ID."""
        with self.lock:
            if app_name not in self.app_states:
                return False
            objects = self.app_states[app_name].get(object_type, [])
            for i, obj in enumerate(objects):
                if obj.get("id") == obj_id:
                    objects.pop(i)
                    self._propagate_event(app_name, "delete", {"type": object_type, "id": obj_id})
                    return True
            return False
    
    def create_shared_object(self, key: str, value: Any) -> None:
        """Create a shared object accessible across apps."""
        with self.lock:
            self.shared_objects[key] = value
            self._propagate_event("global", "shared_object_created", {"key": key})
    
    def get_shared_object(self, key: str) -> Optional[Any]:
        """Get a shared object."""
        with self.lock:
            return self.shared_objects.get(key)
    
    def subscribe_event(self, app_name: str, event_type: str, callback: Callable) -> None:
        """Subscribe to events from an app."""
        with self.lock:
            self.event_listeners[f"{app_name}:{event_type}"].append(callback)
    
    def _propagate_event(self, app_name: str, event_type: str, data: Dict[str, Any]) -> None:
        """Propagate an event to listeners."""
        key = f"{app_name}:{event_type}"
        for callback in self.event_listeners.get(key, []):
            try:
                callback(app_name, event_type, data)
            except Exception as e:
                print(f"Error in event callback: {e}")
    
    def generate_synthetic_data(self, schema: Dict[str, Any], count: int = 1) -> List[Dict[str, Any]]:
        """Generate synthetic data based on a schema."""
        return self.synthetic_data_generator.generate(schema, count)
    
    def clear_app_state(self, app_name: str) -> None:
        """Clear all state for an app."""
        with self.lock:
            if app_name in self.app_states:
                del self.app_states[app_name]


class SyntheticDataGenerator:
    """Generates realistic synthetic data based on schemas."""
    
    def __init__(self):
        from faker import Faker
        self.faker = Faker()
    
    def generate(self, schema: Dict[str, Any], count: int = 1) -> List[Dict[str, Any]]:
        """Generate synthetic data based on JSON schema."""
        results = []
        for _ in range(count):
            result = {}
            properties = schema.get("properties", {})
            for prop_name, prop_schema in properties.items():
                prop_type = prop_schema.get("type")
                if prop_type == "string":
                    if "format" in prop_schema:
                        format_type = prop_schema["format"]
                        if format_type == "email":
                            result[prop_name] = self.faker.email()
                        elif format_type == "date-time":
                            result[prop_name] = self.faker.iso8601()
                        else:
                            result[prop_name] = self.faker.word()
                    else:
                        result[prop_name] = self.faker.sentence()[:50]
                elif prop_type == "integer":
                    min_val = prop_schema.get("minimum", 0)
                    max_val = prop_schema.get("maximum", 1000)
                    result[prop_name] = self.faker.random_int(min=min_val, max=max_val)
                elif prop_type == "number":
                    min_val = prop_schema.get("minimum", 0.0)
                    max_val = prop_schema.get("maximum", 1000.0)
                    result[prop_name] = self.faker.pyfloat(min_value=min_val, max_value=max_val)
                elif prop_type == "boolean":
                    result[prop_name] = self.faker.boolean()
                else:
                    result[prop_name] = self.faker.word()
            results.append(result)
        return results


# Global state engine instance
_state_engine = None

def get_state_engine() -> StateEngine:
    """Get or create the global state engine instance."""
    global _state_engine
    if _state_engine is None:
        _state_engine = StateEngine()
    return _state_engine
