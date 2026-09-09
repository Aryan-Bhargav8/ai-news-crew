from crewai import Crew, Process
from agents import researcher, reporting_analyst
from tasks import reporting_task, research_task
import re
import logging
from pydantic import BaseModel, field_validator


#####################
from fastapi import FastAPI,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

crew = Crew(
    process = Process.sequential,
    verbose = True,
    agents=[researcher,reporting_analyst],
    tasks=[research_task,reporting_task],
)

# now it runs when we request the api

app=FastAPI(title="NewsReporterCrew")
app.add_middleware(
    CORSMiddleware, # to allow cross origin resource sharing meaning that we can access this from any domain
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Only allow plain alphanumeric topics (plus basic punctuation) with a bounded length
# to prevent SSRF via crafted topic strings reaching downstream tools (e.g. SerperDevTool)
TOPIC_PATTERN = re.compile(r"^[A-Za-z0-9 ,.\-']{1,100}$")

class TopicRequest(BaseModel):
    topic: str

    @field_validator("topic")
    @classmethod
    def validate_topic(cls, value: str) -> str:
        value = value.strip()
        if not TOPIC_PATTERN.match(value) or "://" in value or "http" in value.lower():
            raise ValueError("Invalid topic: must be plain text without URLs or special characters")
        return value

@app.get("/")
async def Status():
    status = {"status":"working","message":"API WORKS FINE"}
    return status

@app.post("/run")
async def Run(inputs:TopicRequest):
    """
    Run the CrewAI pipeline with given inputs.
    """
    try:
        # Call your crew with the input
        result = crew.kickoff(inputs={"topic": inputs.topic})
        return {"result": result}
    except Exception as e:
        logging.exception("crew.kickoff failed")
        raise HTTPException(status_code=500, detail="An internal error occurred while processing the request.")
