from agency_swarm.agents import Agent


class ExampleAgent(Agent):
    def __init__(self):
        super().__init__(
            name="ExampleAgent",
            description="Example agent",
            instructions="./instructions.md",
            files_folder="./files",
            schemas_folder="./schemas",
            tools=[],
            tools_folder="./tools",
            temperature=0.3,
            max_prompt_tokens=25000,
        )
