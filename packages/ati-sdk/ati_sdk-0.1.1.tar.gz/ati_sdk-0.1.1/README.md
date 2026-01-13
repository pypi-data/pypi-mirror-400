# ATI SDK

The Core SDK for IOcane ATI (Agent Traffic Intelligence) integrations. This package provides shared utilities for implementing OpenTelemetry instrumentation across various agent frameworks.

## Installation

```bash
pip install ati-sdk
```

## Features

- **`AtiTracer`**: A wrapper around `opentelemetry.trace.Tracer` that enforces ATI semantic conventions.
- **`AtiConfig`**: validation and merging of configuration from environment variables and code.
- **Semantic Conventions**: Constants for standard ATI attributes (`ati.span.type`, etc.).

## Configuration

The SDK reads the following environment variables:

| Variable | Description |
|----------|-------------|
| `ATI_CAPTURE_PAYLOADS` | Enable capturing of input/output payloads (default: `false`) |
| `ATI_REDACTION_ENABLED`| Enable redaction of sensitive data (default: `true`) |
| `ATI_DEBUG` | Enable internal debug logging |

## Usage for Integrators

```python
from ati_sdk import AtiConfig, AtiTracer, AtiSpanType
from opentelemetry.trace import Status, StatusCode

# 1. Initialize Config
config = AtiConfig.from_env()

# 2. Create Tracer
tracer = AtiTracer(framework="mynetwork", tracer_name="ati.myframework", config=config)

# 3. Start Spans
span = tracer.start_span(
    "agent.step",
    AtiSpanType.STEP,
    attributes={"custom.attr": "value"}
)
try:
    # ... execution ...
    pass
except Exception as e:
    span.record_exception(e)
    span.set_status(Status(StatusCode.ERROR))
finally:
    span.end()
```
