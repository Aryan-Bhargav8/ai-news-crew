from crewai import Crew, Process
from agents import researcher, reporting_analyst
from tasks import reporting_task, research_task
import asyncio
import logging

#####################
from fastapi import FastAPI,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator

# now it runs when we request the api

app=FastAPI(title="NewsReporterCrew")

import os
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware, # to allow cross origin resource sharing meaning that we can access this from any domain
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["Content-Type", "Authorization"]
)

class TopicRequest(BaseModel):
    topic: str

    @field_validator('topic')
    @classmethod
    def validate_topic(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError('topic must not be empty')
        if len(v) > 300:
            raise ValueError('topic must not exceed 300 characters')
        import re
        if not re.match(r'^[\w\s\-.,!?()]+$', v):
            raise ValueError('topic contains invalid characters')
        return v

_crew_lock = asyncio.Lock()

def _make_crew():
    return Crew(
        process=Process.sequential,
        verbose=True,
        agents=[researcher, reporting_analyst],
        tasks=[research_task, reporting_task],
    )

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
        async with _crew_lock:
            crew = _make_crew()
            result = crew.kickoff(inputs={"topic": inputs.topic})
        return {"result": result}
    except Exception as e:
        logging.exception("Error running crew pipeline")
        raise HTTPException(status_code=500, detail="An internal server error occurred.")
