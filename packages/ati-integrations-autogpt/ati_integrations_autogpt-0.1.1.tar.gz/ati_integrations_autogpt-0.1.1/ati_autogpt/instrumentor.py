from __future__ import annotations

import functools
from dataclasses import dataclass
from typing import Any, Callable, Optional
import logging

from ati_sdk import AtiConfig, AtiTracer
from ati_sdk.semantics import AtiSpanType, ATI_ATTR
from opentelemetry.trace import Status, StatusCode

logger = logging.getLogger(__name__)

@dataclass
class AutoGPTInstrumentor:
    _enabled: bool = False
    _original_execute_step: Callable | None = None
    _original_agent_class: Any | None = None
    tracer: AtiTracer | None = None

    def instrument(
        self, 
        config: AtiConfig | None = None, 
        agent_module: Any | None = None,
        agent_class: Any | None = None
    ) -> None:
        """
        Instruments AutoGPT agent execution.
        
        Args:
            config: ATI configuration
            agent_module: Optional module containing the Agent class if it cannot be imported from 'autogpt' or 'forge'.
            agent_class: Optional Agent class to instrument directly.
        """
        if self._enabled:
            return
        
        cfg = AtiConfig.from_env().merged(config)
        self.tracer = AtiTracer(framework="autogpt", tracer_name="ati.autogpt", config=cfg)

        # Attempt to resolve Agent class
        target_class = agent_class
        if not target_class:
            if agent_module:
                 target_class = getattr(agent_module, "Agent", None)
            else:
                # Try standard imports
                try:
                    import autogpt.agent
                    target_class = getattr(autogpt.agent, "Agent", None)
                except ImportError:
                    try:
                        import forge.agent
                        target_class = getattr(forge.agent, "Agent", None)
                    except ImportError:
                        pass
        
        if not target_class:
            logger.warning("Could not find AutoGPT Agent class to instrument. Pass agent_class or agent_module explicitly.")
            return

        self._instrument_agent_step(target_class)
        self._enabled = True

    def uninstrument(self) -> None:
        if not self._enabled:
            return
            
        if self._original_execute_step and self._original_agent_class:
            if hasattr(self._original_agent_class, "execute_step"):
                self._original_agent_class.execute_step = self._original_execute_step
            elif hasattr(self._original_agent_class, "step"):
                 self._original_agent_class.step = self._original_execute_step
            
            self._original_execute_step = None
            self._original_agent_class = None

        self._enabled = False

    def _instrument_agent_step(self, agent_class: Any) -> None:
        self._original_agent_class = agent_class
        
        # Identify the step method. Common names: execute_step, step, run_step
        method_name = "execute_step"
        if not hasattr(agent_class, method_name) and hasattr(agent_class, "step"):
            method_name = "step"
        
        if not hasattr(agent_class, method_name):
             logger.warning(f"Agent class {agent_class} has no known step method (execute_step, step).")
             return

        self._original_execute_step = getattr(agent_class, method_name)

        @functools.wraps(self._original_execute_step)
        async def wrapper(agent_instance: Any, *args: Any, **kwargs: Any) -> Any:
            if not self.tracer:
                return await self._original_execute_step(agent_instance, *args, **kwargs)
            
            agent_name = getattr(agent_instance, "ai_name", "autogpt_agent")
            agent_id = str(getattr(agent_instance, "agent_id", agent_name))
            
            span = self.tracer.start_span(
                "autogpt.step",
                AtiSpanType.STEP,
                agent_id=agent_id,
                agent_name=agent_name,
                attributes={
                    ATI_ATTR.step_type: "loop_iteration"
                }
            )

            # Determine task/prompt if available
            # Often args[0] is task or instruction
            if args:
                 payload_content = str(args[0])
                 if self.tracer.config.capture_payloads:
                     self.tracer.add_payload_event(span, kind="step_input", content=payload_content)

            try:
                # Handle both async and sync original methods if needed, but assuming async for modern agents
                if asyncio.iscoroutinefunction(self._original_execute_step):
                    result = await self._original_execute_step(agent_instance, *args, **kwargs)
                else:
                    result = self._original_execute_step(agent_instance, *args, **kwargs)
                
                return result
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR))
                raise
            finally:
                span.end()
        
        setattr(agent_class, method_name, wrapper)

import asyncio
