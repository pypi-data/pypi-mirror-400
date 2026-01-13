# ATI Integration for CrewAI

This package provides OpenTelemetry instrumentation for [CrewAI](https://github.com/joaomdmoura/crewAI) agents using Iocane ATI.

It automatically captures:
- **Agent execution**: Task assignments, inputs, outputs, and execution time.
- **Crew orchestration**: The overall planning and delegation flow.

## Installation

```bash
pip install ati-integrations-crewai opentelemetry-sdk opentelemetry-exporter-otlp
```

## Configuration

Set the standard OpenTelemetry environment variables to point to your Iocane collector:

```bash
export OTEL_EXPORTER_OTLP_ENDPOINT="https://api.iocane.ai/v1/traces"
export OTEL_EXPORTER_OTLP_HEADERS="x-iocane-key=YOUR_KEY,x-ati-env=YOUR_ENV_ID"
export OTEL_SERVICE_NAME="my-crewai-agent"
```

## Usage

Here is the robust pattern for instrumenting CrewAI scripts.

**Important**: Because CrewAI or other libraries might initialize OpenTelemetry internally, it is best practice to *attempt* to set the provider, but always *retrieve* the active global provider to attach your exporters.

```python
import os
from ati_crewai import CrewAIInstrumentor
from crewai import Agent, Crew, Process, Task
from langchain_openai import ChatOpenAI

# OpenTelemetry Imports
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

def main():
    # 1. Configure OpenTelemetry (Robust Pattern)
    resource = Resource.create(attributes={SERVICE_NAME: "my-crew-service"})
    
    try:
        # Try to set the global provider
        provider = TracerProvider(resource=resource)
        trace.set_tracer_provider(provider)
    except Exception:
        # If it fails (e.g., already set), ignore and fetch the active one below
        pass

    # ALWAYS get the global provider to ensure we attach to the active pipeline
    provider = trace.get_tracer_provider()

    # 2. Configure Exporter (Iocane)
    # Ensure usage of the correct endpoint from env or default
    endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT")
    if endpoint and endpoint.endswith("/v1/traces"):
        exporter = OTLPSpanExporter(endpoint=endpoint)
    else:
        exporter = OTLPSpanExporter()
        
    # Check if the provider supports add_span_processor (it typically does)
    if hasattr(provider, "add_span_processor"):
        provider.add_span_processor(BatchSpanProcessor(exporter))
    else:
        print("WARNING: TracerProvider does not support add_span_processor.")

    # 3. Instrument CrewAI
    CrewAIInstrumentor().instrument()

    try:
        # 4. Your CrewAI Code
        llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
        
        agent = Agent(role='Researcher', goal='...', backstory='...', llm=llm)
        task = Task(description='...', agent=agent, expected_output='...')
        crew = Crew(agents=[agent], tasks=[task], verbose=True)

        result = crew.kickoff()
        print(result)

    finally:
        # 5. Uninstrument and Flush
        CrewAIInstrumentor().uninstrument()
        if hasattr(provider, "shutdown"):
            provider.shutdown()

if __name__ == "__main__":
    main()
```

## Environment Variables for Instrumentation

| Variable | Description | Default |
|----------|-------------|---------|
| `ATI_CAPTURE_PAYLOADS` | set to `true` to capture task descriptions and results as span events | `false` |
