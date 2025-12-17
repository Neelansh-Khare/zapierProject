# MCP Universe Simulator

A scalable synthetic universe of mock Zapier-compatible apps for RL agents and AI workflows. Apps simulate realistic schemas, actions, rate limits, triggers, states, authentication flows, errors, and multi-step workflow behavior.

## Overview

This project enables agents to interact with a vast ecosystem of realistic, low-cost, synthetic apps instead of using real APIs. The goal is to build the most comprehensive and realistic MCP mock environment, enabling RL agents and AI systems to practice operating on a diverse ecosystem of apps.

## Key Features

- **Synthetic App Generator**: Generate hundreds of apps from YAML templates or code patterns
- **Universe Randomizer**: Generate random but realistic universes that mimic Zapier's diversity
- **MCP Action Compatibility**: Expose every synthetic app as a valid MCP tool endpoint
- **Chaos Mode**: Inject errors, latency, failures for RL robustness
- **Workflow Orchestrator**: Simulate multi-app workflows internally to validate agent behavior

## Project Structure

```
.
├── core/               # Core engine modules
│   ├── state/         # State engine for app state simulation
│   ├── errors/        # Error simulation and chaos injection
│   └── triggers/      # Trigger system (polling, webhook, scheduled)
├── universe/          # Universe generation and management
│   ├── generator/     # Universe generator logic
│   └── app_registry.json  # Registry of all apps
├── apps/              # Generated app definitions
│   └── <app_name>/    # Individual app folders
├── api/               # API layer
│   └── mcp_exposer/   # MCP server wrapper
└── tools/             # Utility tools
    ├── schema_generator/    # Schema generation utilities
    └── universe_scaler/     # Universe scaling tools
```

## Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

### Creating Example Apps

After installing dependencies, you can generate example apps from the PRD:

```bash
# Install dependencies first
pip install -r requirements.txt

# Generate example apps
python -m tools.create_example_apps
```

This will create 7 example apps (MailoMailer, TaskPad, SheetForge, SalesPulseCRM, Slackette Messaging, AutoBooker Calendar, DriveHive Storage) in the `apps/` directory and register them in `universe/app_registry.json`.

### Using the App Generator

You can programmatically generate apps using the `AppGenerator`:

```python
from core.models import AppCategory, SchemaComplexity, ErrorProfile, LatencyProfile
from tools.schema_generator.app_generator import AppGenerator

generator = AppGenerator()
app = generator.generate_app(
    name="MyApp",
    category=AppCategory.EMAIL,
    action_count=5,
    schema_complexity=SchemaComplexity.MEDIUM,
    error_profile=ErrorProfile.LOW,
    latency_profile=LatencyProfile.NORMAL,
)
```

## Milestones

- **Milestone 1**: Universe generator + 10 apps
- **Milestone 2**: State engine + chaos injection
- **Milestone 3**: MCP server wrapper
- **Milestone 4**: 200 apps output + documentation
- **Milestone 5**: Demo video + README + sample agents

## Development

See `prd.json` for the complete product requirements document.

## License

(To be determined)

