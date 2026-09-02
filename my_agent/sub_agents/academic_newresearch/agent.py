from google.adk import Agent
from . import prompt

academic_newresearch_agent = Agent(
        model="gemini-3.5-flash-lite",
        name="academic_newresearch_agent",
        instruction=prompt.ACADEMIC_NEWRESEARCH_PROMPT,
    )

