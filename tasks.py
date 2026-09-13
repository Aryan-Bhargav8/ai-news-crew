from crewai import Task
from agents import researcher, reporting_analyst
import os
import re

def make_research_task(topic: str) -> Task:
    # Remove any characters that could be interpreted as template syntax
    # by the underlying templating engine (CrewAI), rather than attempting
    # to escape them, since escaping assumes a single templating pass.
    safe_topic = re.sub(r"[{}]", "", topic).strip()
    return Task(
        description=(
            "Conduct a thorough research about "
            + safe_topic
            + "\n        Make sure you find any interesting and relevant information given"
            + "\n        the current year is 2026."
        ),
        expected_output=(
            "A list with 10 bullet points of the most relevant information about "
            + safe_topic
        ),
        agent=researcher
    )

topic = os.environ.get("RESEARCH_TOPIC", "latest developments in AI")
research_task = make_research_task(topic)

reporting_task = Task(
    description="""
        Review the context you got and expand each topic into a full section for a report.
        Make sure the report is detailed and contains any and all relevant information. """,

    expected_output="""
        A fully fledge reports with the mains topics, each with a full section of information.
        Formatted as markdown without '```'""",

    agent=reporting_analyst,

    markdown=True
)