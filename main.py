from crewai import Crew, Process
from agents import researcher, reporting_analyst
from tasks import reporting_task, research_task
import asyncio

#####################
from fastapi import FastAPI,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

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
        raise HTTPException(status_code=500, detail=str(e))
