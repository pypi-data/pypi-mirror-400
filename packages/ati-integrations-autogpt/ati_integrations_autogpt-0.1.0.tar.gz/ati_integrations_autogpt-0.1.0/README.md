# ATI Integration for AutoGPT

This package provides OpenTelemetry instrumentation for AutoGPT-style agents using IOcane ATI.

## Installation

```bash
pip install ati-integrations-autogpt
```

## Usage

```python
from ati_autogpt import AutoGPTInstrumentor
# import your Agent class, e.g. from autogpt.agent import Agent

# 1. Enable Instrumentation
# This wraps the `execute_step` (or `step`) method of the Agent class.
instrumentor = AutoGPTInstrumentor()

# Try to auto-detect 'autogpt.agent.Agent' or 'forge.agent.Agent'
instrumentor.instrument() 

# OR explicitly pass your Agent class
# instrumentor.instrument(agent_class=MyAgent)

# 2. Run your Agent
# agent = Agent(...)
# agent.execute_step(...)

# 3. (Optional) Uninstrument
instrumentor.uninstrument()
```

## Configuration

Configure the instrumentation via environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `ATI_CAPTURE_PAYLOADS` | Capture step inputs | `false` |

## Features
- Captures Agent steps (`ati.span.type=step`)
- Identifies Loop Iterations
