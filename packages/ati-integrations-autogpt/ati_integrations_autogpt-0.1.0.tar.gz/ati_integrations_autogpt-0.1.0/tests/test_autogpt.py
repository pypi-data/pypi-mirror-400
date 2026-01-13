
import pytest
import asyncio
from unittest.mock import MagicMock

from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry import trace

from ati_autogpt import AutoGPTInstrumentor
from ati_sdk.semantics import ATI_ATTR, AtiSpanType

@pytest.fixture
def memory_exporter():
    exporter = InMemorySpanExporter()
    return exporter

# Mock Agent for testing
class MockAgent:
    def __init__(self, ai_name: str):
        self.ai_name = ai_name
    
    async def execute_step(self, instruction):
        return "Done"

@pytest.mark.asyncio
async def test_autogpt_instrumentation(memory_exporter):
    # Setup Tracer
    provider = TracerProvider()
    processor = SimpleSpanProcessor(memory_exporter)
    provider.add_span_processor(processor)

    # Instrument
    instrumentor = AutoGPTInstrumentor()
    instrumentor.uninstrument()
    
    # We pass the MockAgent class directly
    instrumentor.instrument(agent_class=MockAgent)
    
    # Inject local tracer
    instrumentor.tracer.tracer = provider.get_tracer("ati.autogpt")

    try:
        # Create Agent
        agent = MockAgent("TestBot")
        
        # Execute Step
        await agent.execute_step("Do something")
        
        # Verify Spans
        spans = memory_exporter.get_finished_spans()
        assert len(spans) == 1
        span = spans[0]
        assert span.name == "autogpt.step"
        assert span.attributes[ATI_ATTR.span_type] == AtiSpanType.STEP
        assert span.attributes[ATI_ATTR.agent_id] == "TestBot"
        
        # Verify Uninstrument
        instrumentor.uninstrument()
        
        # Helper to check if uninstrumented (original method restored)
        # The wrapper has __wrapped__ if using functools, but we replaced the attribute.
        # We can check if it's a coroutine function if original was one, but wrapper is also one.
        # A simple check: execute again, ensure no new spans.
        
        memory_exporter.clear()
        await agent.execute_step("Do something else")
        assert len(memory_exporter.get_finished_spans()) == 0

    finally:
        instrumentor.uninstrument()
