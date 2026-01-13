import os
from crewai import Agent, Task, Crew, Process
# Use ChatOpenAI for the example
from langchain_openai import ChatOpenAI
from ati_crewai import CrewAIInstrumentor

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter, SimpleSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

def main():
    # 1. Configure OpenTelemetry
    resource = Resource.create(attributes={SERVICE_NAME: "ati-crewai-example"})

    # Attempt to set the global provider
    try:
        new_provider = TracerProvider(resource=resource)
        trace.set_tracer_provider(new_provider)
    except Exception:
        # If this fails or warns, we ignore it and fetch the current global one below
        pass

    # CRITICAL FIX: Always get the global provider. 
    # If set_tracer_provider worked, this returns our new_provider.
    # If it failed (silently or with exception), this returns the pre-existing global provider.
    provider = trace.get_tracer_provider()
    
    print(f"DEBUG: Using TracerProvider {id(provider)} type {type(provider)}")

    # CRITICAL FIX: Always get the global provider. 
    # If set_tracer_provider worked, this returns our new_provider.
    # If it failed (silently or with exception), this returns the pre-existing global provider.
    provider = trace.get_tracer_provider()

    endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT")
    if endpoint and endpoint.endswith("/v1/traces"):
        exporter = OTLPSpanExporter(endpoint=endpoint)
    else:
        exporter = OTLPSpanExporter()
        
    # Check if we can add a processor (SDK provider)
    if hasattr(provider, "add_span_processor"):
        provider.add_span_processor(BatchSpanProcessor(exporter))
        # Optional: Add Console exporter for local visibility
        provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
    else:
        print(f"WARNING: TracerProvider {type(provider)} does not support add_span_processor. Traces may not be exported.")

    # 2. Instrument
    print("Instrumenting CrewAI...")
    CrewAIInstrumentor().instrument()

    try:
        # 3. Setup LLM
        # We use a real LLM (gpt-3.5-turbo)
        llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

        # 4. Define Agents
        researcher = Agent(
            role='Researcher',
            goal='Analyze ATI',
            backstory='Expert researcher',
            llm=llm,
            verbose=True,
            allow_delegation=False
        )
        
        # 5. Define Tasks
        task = Task(
            description='Analyze the ATI project structure.',
            agent=researcher,
            expected_output='A report.'
        )

        # 6. Define Crew
        crew = Crew(
            agents=[researcher],
            tasks=[task],
            process=Process.sequential,
            verbose=True
        )

        # 7. Kickoff
        print("\n--- Starting Crew Kickoff ---\n")
        result = crew.kickoff()
        print(f"\nResult: {result}")
    
    finally:
        # 8. Uninstrument and Flush
        CrewAIInstrumentor().uninstrument()
        if hasattr(provider, "shutdown"):
            provider.shutdown()
        else:
            print(f"WARNING: Provider {type(provider)} does not have shutdown method.")

if __name__ == "__main__":
    main()
