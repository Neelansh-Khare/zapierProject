"""Trigger system for polling, webhook, and scheduled triggers."""
import asyncio
import time
from typing import Dict, List, Callable, Optional, Any
from enum import Enum
from datetime import datetime, timedelta


class TriggerType(Enum):
    POLLING = "polling"
    WEBHOOK = "webhook"
    SCHEDULED = "scheduled"


class Trigger:
    """Represents a trigger configuration."""
    
    def __init__(
        self,
        trigger_id: str,
        app_name: str,
        trigger_type: TriggerType,
        callback: Callable,
        frequency_seconds: Optional[int] = None,
        condition: Optional[Callable] = None,
        enabled: bool = True
    ):
        self.trigger_id = trigger_id
        self.app_name = app_name
        self.trigger_type = trigger_type
        self.callback = callback
        self.frequency_seconds = frequency_seconds or 60
        self.condition = condition
        self.enabled = enabled
        self.last_fired = None
        self.fire_count = 0
    
    async def fire(self) -> Any:
        """Fire the trigger if conditions are met."""
        if not self.enabled:
            return None
        
        if self.condition and not self.condition():
            return None
        
        self.last_fired = datetime.now()
        self.fire_count += 1
        
        if asyncio.iscoroutinefunction(self.callback):
            return await self.callback()
        else:
            return self.callback()


class TriggerSystem:
    """Manages triggers for apps."""
    
    def __init__(self):
        self.triggers: Dict[str, Trigger] = {}
        self.webhook_endpoints: Dict[str, str] = {}  # app_name -> endpoint
        self.running = False
        self._polling_task: Optional[asyncio.Task] = None
    
    def register_trigger(
        self,
        app_name: str,
        trigger_type: TriggerType,
        callback: Callable,
        frequency_seconds: Optional[int] = None,
        condition: Optional[Callable] = None
    ) -> str:
        """Register a new trigger."""
        trigger_id = f"{app_name}_{trigger_type.value}_{len(self.triggers)}" 
        trigger = Trigger(
            trigger_id=trigger_id,
            app_name=app_name,
            trigger_type=trigger_type,
            callback=callback,
            frequency_seconds=frequency_seconds,
            condition=condition
        )
        self.triggers[trigger_id] = trigger
        
        if trigger_type == TriggerType.WEBHOOK:
            endpoint = f"/webhook/{app_name}/{trigger_id}"
            self.webhook_endpoints[trigger_id] = endpoint
        
        return trigger_id
    
    def unregister_trigger(self, trigger_id: str) -> None:
        """Unregister a trigger."""
        if trigger_id in self.triggers:
            del self.triggers[trigger_id]
        if trigger_id in self.webhook_endpoints:
            del self.webhook_endpoints[trigger_id]
    
    def enable_trigger(self, trigger_id: str) -> None:
        """Enable a trigger."""
        if trigger_id in self.triggers:
            self.triggers[trigger_id].enabled = True
    
    def disable_trigger(self, trigger_id: str) -> None:
        """Disable a trigger."""
        if trigger_id in self.triggers:
            self.triggers[trigger_id].enabled = False
    
    async def start_polling(self) -> None:
        """Start the polling loop for polling and scheduled triggers."""
        self.running = True
        while self.running:
            await asyncio.sleep(1)  # Check every second
            now = datetime.now()
            
            for trigger in self.triggers.values():
                if not trigger.enabled:
                    continue
                
                if trigger.trigger_type == TriggerType.POLLING:
                    if trigger.last_fired is None or \
                       (now - trigger.last_fired).total_seconds() >= trigger.frequency_seconds:
                        try:
                            await trigger.fire()
                        except Exception as e:
                            print(f"Error firing trigger {trigger.trigger_id}: {e}")
                
                elif trigger.trigger_type == TriggerType.SCHEDULED:
                    if trigger.last_fired is None or \
                       (now - trigger.last_fired).total_seconds() >= trigger.frequency_seconds:
                        try:
                            await trigger.fire()
                        except Exception as e:
                            print(f"Error firing scheduled trigger {trigger.trigger_id}: {e}")
    
    def stop_polling(self) -> None:
        """Stop the polling loop."""
        self.running = False
    
    async def fire_webhook(self, trigger_id: str, data: Dict[str, Any]) -> Any:
        """Fire a webhook trigger."""
        if trigger_id in self.triggers:
            trigger = self.triggers[trigger_id]
            if trigger.trigger_type == TriggerType.WEBHOOK:
                return await trigger.fire()
        return None
    
    def get_webhook_endpoint(self, trigger_id: str) -> Optional[str]:
        """Get webhook endpoint for a trigger."""
        return self.webhook_endpoints.get(trigger_id)
    
    def get_app_triggers(self, app_name: str) -> List[Trigger]:
        """Get all triggers for an app."""
        return [
            trigger for trigger in self.triggers.values()
            if trigger.app_name == app_name
        ]


# Global trigger system instance
_trigger_system = None

def get_trigger_system() -> TriggerSystem:
    """Get or create the global trigger system instance."""
    global _trigger_system
    if _trigger_system is None:
        _trigger_system = TriggerSystem()
    return _trigger_system
