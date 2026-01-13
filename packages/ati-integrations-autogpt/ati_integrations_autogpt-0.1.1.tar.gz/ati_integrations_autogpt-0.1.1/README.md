# ATI Integration for AutoGPT

This package provides OpenTelemetry instrumentation for AutoGPT-style agents using IOcane ATI.

## Installation

```bash
pip install ati-integrations-autogpt opentelemetry-sdk opentelemetry-exporter-otlp
```

## Configuration

Set the standard OpenTelemetry environment variables:

```bash
export OTEL_EXPORTER_OTLP_ENDPOINT="https://api.iocane.ai"
export OTEL_EXPORTER_OTLP_HEADERS="x-iocane-key=YOUR_KEY,x-ati-env=YOUR_ENV_ID"
export OTEL_SERVICE_NAME="my-autogpt-agent"
```

## Usage

```python
import os
from ati_autogpt import AutoGPTInstrumentor
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

# 1. Configure OpenTelemetry
provider = TracerProvider()
exporter = OTLPSpanExporter()
provider.add_span_processor(BatchSpanProcessor(exporter))
trace.set_tracer_provider(provider)

# 2. Instrument AutoGPT
instrumentor = AutoGPTInstrumentor()
instrumentor.instrument() # auto-detects Agent class

# 3. Run your Agent
# ...

# 4. Flush traces
provider.shutdown()
```

## Configuration

Configure the instrumentation via environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `ATI_CAPTURE_PAYLOADS` | Capture step inputs | `false` |

## Features
- Captures Agent steps (`ati.span.type=step`)
- Identifies Loop Iterations
