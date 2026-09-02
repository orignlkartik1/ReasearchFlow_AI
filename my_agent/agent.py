from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool

from . import prompt
from .sub_agents.academic_newresearch.agent import academic_newresearch_agent
from .sub_agents.academic_webresearch.agent import create_academic_websearch_agent


root_agent = Agent(
        name="academic_coordinator",
        model='gemini-3.5-flash-lite',
        description=(
            "Analyzes seminal papers provided by users, provides research advice, "
            "locates current papers relevant to the seminal paper, generates suggestions "
            "for new research directions, and accesses web resources to acquire knowledge."
        ),
        instruction=prompt.ACADEMIC_COORDINATOR_PROMPT,
        output_key="seminal_paper",
        tools=[
            AgentTool(agent=academic_newresearch_agent),
            AgentTool(agent=create_academic_newresearch_agent(llm_model)),
        ],
    )

