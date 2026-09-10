import os
import re
from crewai import Agent, LLM
from crewai_tools import SerperDevTool
from dotenv import load_dotenv
load_dotenv()

GROQ_API_KEY = os.getenv('GROQ_API_KEY')
MODEL = os.getenv("MODEL")
SERPER_API_KEY= os.getenv("SERPER_API_KEY")

llm = LLM(
    model=MODEL,
    api_key=GROQ_API_KEY,
    temperature=0,
    reasoning_effort="medium",
)


def sanitize_topic(topic: str) -> str:
    """Remove search operator injections and control characters from topic."""
    # Strip known search operators (site:, OR, AND, filetype:, inurl:, intitle:, etc.)
    topic = re.sub(r'\b(site|filetype|inurl|intitle|intext|cache|related|OR|AND|NOT)\s*:', '', topic, flags=re.IGNORECASE)
    # Remove characters commonly used to chain or inject search operators
    topic = re.sub(r'[|&+"\\<>]', ' ', topic)
    # Collapse whitespace
    topic = re.sub(r'\s+', ' ', topic).strip()
    return topic


researcher = Agent(
    role = "Senior Data Researcher",
    goal = "Uncover cutting-edge developments in {topic}",  # topic is sanitized at kickoff
    backstory = """
    You're a seasoned researcher with a knack for uncovering the latest
    developments in {topic}.
    Known for your ability to find the most relevant information
    and present it in a clear and concise manner.
    Use the SerperDevTool to get the most recent information available.""",
    llm = llm,
    verbose = True,
    tools=[
        SerperDevTool(
            n_results=20
        )
    ]
)


reporting_analyst = Agent(
    role = "Reporting Analyst",
    goal = "Create detailed reports based on {topic} data analysis and research findings",
    backstory = """
    You're a meticulous analyst with a keen eye for detail.
    You're known for your ability to turn complex data into clear and concise reports, making
    it easy for others to understand and act on the information you provide.""",
    llm = llm,
    verbose = True
)