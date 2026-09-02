from google.adk import Agent
from . import prompt

academic_newresearch_agent = Agent(
        model="gemini-2.5-flash",
        name="academic_newresearch_agent",
        instruction=prompt.ACADEMIC_NEWRESEARCH_PROMPT,
    )

