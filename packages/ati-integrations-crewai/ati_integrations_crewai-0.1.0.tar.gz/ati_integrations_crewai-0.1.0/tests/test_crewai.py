
import pytest
from unittest.mock import patch, MagicMock
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry import trace

import crewai
from crewai import Agent, Task, Crew, Process
from langchain_community.llms import FakeListLLM

from ati_crewai import CrewAIInstrumentor
from ati_sdk.semantics import ATI_ATTR, AtiSpanType

@pytest.fixture
def memory_exporter():
    exporter = InMemorySpanExporter()
    return exporter

def test_crewai_instrumentation(memory_exporter):
    # Setup - Mocking internals to avoid LLM calls
    original_execute = crewai.Agent.execute_task
    original_kickoff = crewai.Crew.kickoff

    # Define mocks that simulate successful execution
    def mock_kickoff(self, *args, **kwargs):
        # Simulate walking through tasks
        for task in self.tasks:
            if task.agent:
                task.agent.execute_task(task)
        return "Crew Finished"
    
    def mock_execute_task(self, task, *args, **kwargs):
        return "Task Finished"

    # Patch the class methods
    crewai.Crew.kickoff = mock_kickoff
    crewai.Agent.execute_task = mock_execute_task

    # Bypass OpenAI API Key check
    import os
    os.environ["OPENAI_API_KEY"] = "fake"

    try:
        # Trace Provider Setup
        provider = TracerProvider()
        processor = SimpleSpanProcessor(memory_exporter)
        provider.add_span_processor(processor)

        # Instrument (this wraps our mocks)
        instrumentor = CrewAIInstrumentor()
        instrumentor.uninstrument()
        instrumentor.instrument()
        
        # Inject our local tracer
        instrumentor.tracer.tracer = provider.get_tracer("ati.crewai")

        # Create dummy objects
        agent = Agent(
            role='Tester',
            goal='Test',
            backstory='Tester',
            allow_delegation=False,
            formatted_backstory='Tester'
        )
        
        task = Task(
            description='Test task',
            agent=agent,
            expected_output='Done'
        )

        crew = Crew(
            agents=[agent],
            tasks=[task],
            process=Process.sequential
        )

        # Execution
        crew.kickoff()

        # Verification
        spans = memory_exporter.get_finished_spans()
        
        assert len(spans) >= 2
        
        crew_span = next((s for s in spans if s.name == "crewai.crew.kickoff"), None)
        assert crew_span is not None
        assert crew_span.attributes[ATI_ATTR.span_type] == AtiSpanType.AGENT
        assert crew_span.attributes[ATI_ATTR.agent_role] == "orchestrator"
        
        agent_span = next((s for s in spans if s.name == "crewai.agent.execute"), None)
        assert agent_span is not None
        assert agent_span.attributes[ATI_ATTR.span_type] == AtiSpanType.AGENT
        assert agent_span.attributes[ATI_ATTR.agent_role] == "Tester"

        instrumentor.uninstrument()
        
        # Verify uninstrumentation restored our mocks
        assert crewai.Crew.kickoff == mock_kickoff
        assert crewai.Agent.execute_task == mock_execute_task

    finally:
        # Restore original methods
        crewai.Crew.kickoff = original_kickoff
        crewai.Agent.execute_task = original_execute
        # Optional: Unset env var if needed, but safe with fake
        if os.environ.get("OPENAI_API_KEY") == "fake":
            del os.environ["OPENAI_API_KEY"]
