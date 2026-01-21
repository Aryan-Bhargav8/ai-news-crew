import os
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


researcher = Agent(
    role = "Senior Data Researcher",
    goal = "Uncover cutting-edge developments in {topic}",
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