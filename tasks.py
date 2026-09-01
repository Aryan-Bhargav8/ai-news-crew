from crewai import Task
from agents import researcher, reporting_analyst

def make_research_task(topic: str) -> Task:
    safe_topic = topic.replace("{", "{{{").replace("}", "}}}")
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

research_task = make_research_task

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