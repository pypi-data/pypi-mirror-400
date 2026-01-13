
import asyncio
from ati_autogpt import AutoGPTInstrumentor

# Mock AutoGPT Agent class
class Agent:
    def __init__(self, ai_name: str):
        self.ai_name = ai_name

    async def execute_step(self, instruction: str):
        print(f"[{self.ai_name}] Executing step: {instruction}")
        await asyncio.sleep(0.1)
        return "Step completed"

async def main():
    # 1. Instrument
    instrumentor = AutoGPTInstrumentor()
    # Pass our mock class explicitly since we don't have 'autogpt' installed
    instrumentor.instrument(agent_class=Agent)

    # 2. Run Agent
    agent = Agent(ai_name="AutoGPT_Mock")
    await agent.execute_step("Research ATI integrations")

    # 3. Uninstrument
    instrumentor.uninstrument()
    print("Finished.")

if __name__ == "__main__":
    asyncio.run(main())
