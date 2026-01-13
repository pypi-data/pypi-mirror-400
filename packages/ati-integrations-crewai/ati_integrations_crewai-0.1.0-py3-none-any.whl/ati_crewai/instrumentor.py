from __future__ import annotations

import functools
from dataclasses import dataclass
from typing import Any, Callable

import crewai
from opentelemetry.trace import Status, StatusCode
from ati_sdk import AtiConfig, AtiTracer
from ati_sdk.semantics import AtiSpanType, ATI_ATTR

@dataclass
class CrewAIInstrumentor:
    _enabled: bool = False
    _original_kickoff: Callable | None = None
    _original_execute_task: Callable | None = None
    tracer: AtiTracer | None = None

    def instrument(self, config: AtiConfig | None = None) -> None:
        if self._enabled:
            return

        cfg = AtiConfig.from_env().merged(config)
        self.tracer = AtiTracer(framework="crewai", tracer_name="ati.crewai", config=cfg)
        
        self._instrument_crew_kickoff()
        self._instrument_agent_execute_task()
        
        self._enabled = True

    def uninstrument(self) -> None:
        if not self._enabled:
            return

        if self._original_kickoff:
            crewai.Crew.kickoff = self._original_kickoff
            self._original_kickoff = None
        
        if self._original_execute_task:
            crewai.Agent.execute_task = self._original_execute_task
            self._original_execute_task = None
            
        self._enabled = False

    def _instrument_crew_kickoff(self) -> None:
        self._original_kickoff = crewai.Crew.kickoff
        
        @functools.wraps(self._original_kickoff)
        def wrapper(crew_instance: crewai.Crew, *args: Any, **kwargs: Any) -> Any:
            if not self.tracer:
                return self._original_kickoff(crew_instance, *args, **kwargs)

            # Use crew ID or generating one if missing
            agent_id = str(getattr(crew_instance, "id", "crew_unknown"))
            # Crew usually doesn't have a name attribute, maybe verify
            
            span = self.tracer.start_span(
                "crewai.crew.kickoff",
                AtiSpanType.AGENT,
                agent_id=agent_id,
                agent_role="orchestrator",
                attributes={
                    # "ati.crew.process": str(crew_instance.process)
                }
            )
            
            try:
                result = self._original_kickoff(crew_instance, *args, **kwargs)
                return result
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR))
                raise
            finally:
                span.end()
                
        crewai.Crew.kickoff = wrapper

    def _instrument_agent_execute_task(self) -> None:
        self._original_execute_task = crewai.Agent.execute_task
        
        @functools.wraps(self._original_execute_task)
        def wrapper(agent_instance: crewai.Agent, task: Any, *args: Any, **kwargs: Any) -> Any:
            if not self.tracer:
                return self._original_execute_task(agent_instance, task, *args, **kwargs)

            # Agent usually has role, goal, backstory
            agent_name = getattr(agent_instance, "role", "unknown_agent")
            agent_role = getattr(agent_instance, "role", "worker")
            # In CrewAI, agents are often identified by role or role+goal.
            
            # Using role as ID for now if no explicit ID
            agent_id = str(getattr(agent_instance, "id", agent_name))

            task_desc = getattr(task, "description", "")
            
            span = self.tracer.start_span(
                "crewai.agent.execute",
                AtiSpanType.AGENT, # Agent execution of a task
                agent_id=agent_id,
                agent_name=agent_name,
                agent_role=agent_role,
                attributes={
                     ATI_ATTR.step_type: "worker", # It's doing work
                }
            )
            
            # Add task description as payload/event? Or attribute if short?
            # Privacy safe: attribute only if short, or payload if enabled.
            if self.tracer.config.capture_prompts or self.tracer.config.capture_payloads:
                 self.tracer.add_payload_event(
                     span,
                     kind="task_description",
                     content=task_desc,
                     redaction_patterns=(),
                     enabled=True
                 )

            try:
                result = self._original_execute_task(agent_instance, task, *args, **kwargs)
                return result
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR))
                raise
            finally:
                span.end()
                
        crewai.Agent.execute_task = wrapper
