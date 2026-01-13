import os
import asyncio
from ati_autogpt import AutoGPTInstrumentor

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

# Mock AutoGPT Agent class
class Agent:
    def __init__(self, ai_name: str):
        self.ai_name = ai_name

    async def execute_step(self, instruction: str):
        print(f"[{self.ai_name}] Executing step: {instruction}")
        await asyncio.sleep(0.1)
        return "Step completed"

async def main():
    # 1. Configure OpenTelemetry
    provider = TracerProvider()
    endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT")
    if endpoint and endpoint.endswith("/v1/traces"):
        exporter = OTLPSpanExporter(endpoint=endpoint)
    else:
        exporter = OTLPSpanExporter()
        
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)

    # 2. Instrument
    instrumentor = AutoGPTInstrumentor()
    # Pass our mock class explicitly since we don't have 'autogpt' installed
    instrumentor.instrument(agent_class=Agent)

    try:
        # 3. Run Agent
        agent = Agent(ai_name="AutoGPT_Mock")
        await agent.execute_step("Research ATI integrations")
    finally:
        # 4. Cleanup
        instrumentor.uninstrument()
        provider.shutdown()
        print("Finished.")

if __name__ == "__main__":
    asyncio.run(main())
