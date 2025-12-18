"""Basic usage examples for MCP Universe Simulator."""
import asyncio
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from universe.app_loader import get_app_loader
from core.app_runtime import AppRuntime


async def example_execute_action():
    """Example: Execute an action on an app."""
    app_loader = get_app_loader()
    
    # Load MailoMailer app
    app = app_loader.load_app("MailoMailer")
    if not app:
        print("MailoMailer app not found. Please run 'python -m tools.create_example_apps' first.")
        return
    
    # Create runtime for the app
    runtime = AppRuntime(app)
    
    # Send an email
    result = await runtime.execute_action(
        "send_email",
        {
            "to": "user@example.com",
            "subject": "Hello from MCP Universe",
            "body": "This is a test email sent through the synthetic MailoMailer app!"
        }
    )
    
    print("Email send result:")
    print(result)
    
    # List emails
    list_result = await runtime.execute_action(
        "list_emails",
        {
            "limit": 10
        }
    )
    
    print("\nEmail list result:")
    print(list_result)


async def example_task_management():
    """Example: Task management with TaskPad."""
    app_loader = get_app_loader()
    app = app_loader.load_app("TaskPad")
    
    if not app:
        print("TaskPad app not found. Please run 'python -m tools.create_example_apps' first.")
        return
    
    runtime = AppRuntime(app)
    
    # Create a task
    create_result = await runtime.execute_action(
        "create_task",
        {
            "title": "Complete MCP Universe implementation",
            "description": "Finish all the core features",
            "priority": "high"
        }
    )
    
    print("Task creation result:")
    print(create_result)
    
    if create_result.get("success"):
        task_id = create_result["result"].get("id")
        
        if task_id:
            # Update the task
            update_result = await runtime.execute_action(
                "update_task",
                {
                    "id": task_id,
                    "status": "in_progress"
                }
            )
            
            print("\nTask update result:")
            print(update_result)
            
            # List tasks
            list_result = await runtime.execute_action(
                "list_tasks",
                {"limit": 10}
            )
            
            print("\nTask list result:")
            print(list_result)


async def example_multiple_apps():
    """Example: Using multiple apps together."""
    app_loader = get_app_loader()
    
    # Create a task in TaskPad
    task_app = app_loader.load_app("TaskPad")
    if task_app:
        task_runtime = AppRuntime(task_app)
        task_result = await task_runtime.execute_action(
            "create_task",
            {"title": "Send welcome email", "priority": "high"}
        )
        print("Created task:", task_result)
    
    # Send email via MailoMailer
    email_app = app_loader.load_app("MailoMailer")
    if email_app:
        email_runtime = AppRuntime(email_app)
        email_result = await email_runtime.execute_action(
            "send_email",
            {
                "to": "newuser@example.com",
                "subject": "Welcome!",
                "body": "Welcome to our platform!"
            }
        )
        print("Sent email:", email_result)
    
    # Create calendar event
    calendar_app = app_loader.load_app("AutoBooker Calendar")
    if calendar_app:
        calendar_runtime = AppRuntime(calendar_app)
        event_result = await calendar_runtime.execute_action(
            "create_event",
            {
                "title": "Team Meeting",
                "start_time": "2024-01-15T10:00:00Z",
                "end_time": "2024-01-15T11:00:00Z"
            }
        )
        print("Created event:", event_result)


def example_list_apps():
    """Example: List all available apps."""
    app_loader = get_app_loader()
    apps = app_loader.get_all_apps()
    
    print(f"Available apps ({len(apps)}):")
    for app in apps:
        print(f"  - {app.metadata.name} ({app.metadata.category.value}): {app.metadata.description}")
        action_names = [action.name for action in app.actions]
        print(f"    Actions: {', '.join(action_names)}")


async def example_universe_generation():
    """Example: Generate a universe of apps."""
    from universe.config import UniverseConfig
    from tools.universe_scaler.scaler import UniverseScaler
    from core.models import AppCategory
    
    # Create custom config
    config = UniverseConfig(
        num_apps=10,
        categories_enabled=[AppCategory.EMAIL, AppCategory.STORAGE, AppCategory.PRODUCTIVITY],
        chaos_level=1.5
    )
    
    # Generate universe
    scaler = UniverseScaler(config)
    universe = scaler.scale_universe(10)
    
    print(f"Generated {universe['total_apps']} apps")
    print(f"Categories: {[cat.value for cat in config.categories_enabled]}")


if __name__ == "__main__":
    print("=== MCP Universe Simulator Examples ===\n")
    
    print("1. Listing all apps:")
    example_list_apps()
    
    print("\n2. Executing actions:")
    asyncio.run(example_execute_action())
    
    print("\n3. Task management:")
    asyncio.run(example_task_management())
    
    print("\n4. Multi-app workflow:")
    asyncio.run(example_multiple_apps())
    
    print("\n5. Universe generation:")
    asyncio.run(example_universe_generation())

