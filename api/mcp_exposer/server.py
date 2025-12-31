"""
MCP server wrapper exposing apps as MCP tools.
"""
from typing import Dict, List, Any, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from universe.app_loader import get_app_loader
from core.app_runtime import AppRuntime
from core.errors.simulator import get_error_simulator
from core.models import AppCategory

class ActionResponse(BaseModel):
    """Response model for action execution."""
    success: bool
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    latency_ms: Optional[int] = None


class MCPExposer:
    """Exposes synthetic apps as MCP-compatible tools."""
    
    def __init__(self):
        self.app_loader = get_app_loader()
        self.app = FastAPI(
            title="MCP Universe Simulator",
            description="A scalable synthetic universe of mock Zapier-compatible apps.",
            version="1.0.0"
        )
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup API routes."""
        
        @self.app.get("/")
        async def root():
            return {
                "name": "MCP Universe Simulator",
                "version": "1.0.0",
                "status": "running"
            }
        
        @self.app.get("/apps")
        async def list_apps():
            """List all available apps."""
            apps = self.app_loader.get_all_apps()
            return {
                "apps": [
                    {
                        "name": app.metadata.name,
                        "category": app.metadata.category,
                        "description": app.metadata.description,
                        "actions": [action.name for action in app.actions]
                    }
                    for app in apps
                ],
                "total": len(apps)
            }
        
        @self.app.get("/apps/{app_name}")
        async def get_app(app_name: str):
            """Get app details."""
            app = self.app_loader.load_app(app_name)
            if not app:
                raise HTTPException(status_code=404, detail=f"App '{app_name}' not found")
            
            return app.to_dict()
        
        @self.app.get("/apps/{app_name}/actions/{action_name}")
        async def get_action_schema(app_name: str, action_name: str):
            """Get action schema."""
            app = self.app_loader.load_app(app_name)
            if not app:
                raise HTTPException(status_code=404, detail=f"App '{app_name}' not found")
            
            action = app.get_action(action_name)
            if not action:
                raise HTTPException(
                    status_code=404,
                    detail=f"Action '{action_name}' not found in app '{app_name}'"
                )
            
            return action.model_dump(mode="json")
        
        @self.app.post("/apps/{app_name}/actions/{action_name}/execute")
        async def execute_action(app_name: str, action_name: str, request: Dict[str, Any]):
            """Execute an action."""
            app = self.app_loader.load_app(app_name)
            if not app:
                raise HTTPException(status_code=404, detail=f"App '{app_name}' not found")

            runtime = AppRuntime(app)
            inputs = request.get("inputs", {})
            result = await runtime.execute_action(action_name, inputs)
            
            return result

        @self.app.get("/tools")
        async def list_tools():
            """List all available MCP tools (app actions)."""
            tools = []
            apps = self.app_loader.get_all_apps()
            
            for app in apps:
                for action in app.actions:
                    tool = {
                        "name": f"{app.metadata.name.replace(' ', '_')}_{action.name}",
                        "description": f"{app.metadata.description} - {action.name}",
                        "app": app.metadata.name,
                        "action": action.name,
                        "inputSchema": action.inputs_schema,
                        "outputSchema": action.outputs_schema
                    }
                    tools.append(tool)
            
            return {
                "tools": tools,
                "total": len(tools)
            }

        @self.app.post("/tools/{tool_name}/call")
        async def call_tool(tool_name: str, arguments: Dict[str, Any]):
            """Call a tool (MCP-compatible)."""
            
            # Find the app that matches the tool name prefix
            apps = self.app_loader.get_all_apps()
            target_app = None
            action_name = None
            
            for app in apps:
                app_prefix = app.metadata.name.replace(' ', '_')
                if tool_name.startswith(app_prefix + "_"):
                    # Found a potential match
                    possible_action = tool_name[len(app_prefix)+1:]
                    # Verify this action exists in the app
                    if app.get_action(possible_action):
                        target_app = app
                        action_name = possible_action
                        break
            
            if not target_app or not action_name:
                # Fallback to old splitting logic just in case, or fail
                try:
                    app_name_str, action_part = tool_name.rsplit("_", 1)
                    app_name_fallback = app_name_str.replace('_', ' ')
                    target_app = self.app_loader.load_app(app_name_fallback)
                    action_name = action_part
                except ValueError:
                    pass

            if not target_app:
                raise HTTPException(status_code=404, detail=f"App not found for tool '{tool_name}'")

            runtime = AppRuntime(target_app)
            result = await runtime.execute_action(action_name, arguments)

            if not result.get("success"):
                raise HTTPException(
                    status_code=500,
                    detail={
                        "error": result.get("error"),
                        "message": result.get("error", {}).get("message", "Action execution failed")
                    }
                )
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": str(result.get("result"))
                    }
                ]
            }

        @self.app.get("/categories")
        async def list_categories():
            """List all app categories."""
            return {
                "categories": [c.value for c in AppCategory],
                "total": len(AppCategory)
            }

        @self.app.post("/chaos")
        async def set_chaos_mode(chaos_level: Dict[str, float]):
            """Set chaos mode level."""
            level = chaos_level.get("level", 1.0)
            error_simulator = get_error_simulator()
            error_simulator.set_chaos_mode(level)
            
            return {
                "chaos_level": level,
                "message": f"Chaos mode set to {level}"
            }

    def get_app(self) -> FastAPI:
        """Get the FastAPI app."""
        return self.app


def create_mcp_server() -> FastAPI:
    """Create and return MCP server instance."""
    exposer = MCPExposer()
    return exposer.get_app()


# Expose app for uvicorn
app = create_mcp_server()
