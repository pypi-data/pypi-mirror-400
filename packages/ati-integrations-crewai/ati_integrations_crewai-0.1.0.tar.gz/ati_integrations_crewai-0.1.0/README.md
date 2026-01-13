# ATI Integration for CrewAI

This package provides OpenTelemetry instrumentation for CrewAI agents using IOcane ATI.

## Installation

```bash
pip install ati-integrations-crewai
```

## Usage

```python
from ati_crewai import CrewAIInstrumentor
from crewai import Agent, Task, Crew

# 1. Enable Instrumentation
# This monkeyspatches Crew.kickoff and Agent.execute_task
instrumentor = CrewAIInstrumentor()
instrumentor.instrument()

# 2. Run your Crew as normal
# ... define agents and tasks ...
crew = Crew(agents=[...], tasks=[...])
crew.kickoff()

# 3. (Optional) Disable instrumentation
instrumentor.uninstrument()
```

## Configuration

Configure the instrumentation via environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `ATI_CAPTURE_PAYLOADS` | Capture task descriptions and results | `false` |

## Features
- Captures Crew execution (Orchestrator)
- Captures Agent task execution (Worker)
- Automatic context propagation
