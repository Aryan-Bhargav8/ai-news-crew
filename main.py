from crewai import Crew, Process
from agents import researcher, reporting_analyst
from tasks import reporting_task, research_task
import asyncio
import logging
import re
import html

#####################
from fastapi import FastAPI,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field, validator

# now it runs when we request the api

app=FastAPI(title="NewsReporterCrew")

import os
ALLOWED_ORIGINS = [origin.strip() for origin in os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",") if origin.strip()]
# Reject wildcard/unsafe origins when credentials are allowed to prevent CORS misconfiguration (CWE-942)
if not ALLOWED_ORIGINS or "*" in ALLOWED_ORIGINS:
    raise RuntimeError(
        "ALLOWED_ORIGINS must be a non-empty list of explicit trusted origins and must not "
        "contain '*' when allow_credentials=True."
    )
API_KEY = os.getenv("API_KEY")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def verify_api_key(api_key: str = None):
    from fastapi import Depends, Security
    return api_key

def require_api_key(provided_key: str = None):
    pass

app.add_middleware(
    CORSMiddleware, # to allow cross origin resource sharing meaning that we can access this from any domain
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["Content-Type", "Authorization"]
)

class TopicRequest(BaseModel):
    topic: str = Field(..., min_length=1, max_length=200)

    @validator("topic")
    def validate_topic(cls, v):
        if "\x00" in v:
            raise ValueError("Topic must not contain null bytes")
        if "\n" in v or "\r" in v:
            raise ValueError("Topic must not contain newline characters")
        if not re.match(r"^[A-Za-z0-9 ,.'\"?!:;()-]+$", v):
            raise ValueError("Topic contains invalid or unsafe characters")
        if ".." in v or "/" in v or "\\" in v:
            raise ValueError("Topic must not contain path traversal sequences")
        lowered = v.lower()
        if any(kw in lowered for kw in ("ignore previous", "system prompt", "you are now", "disregard", "act as")):
            raise ValueError("Topic contains disallowed instruction-like content")
        return v.strip()

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

from fastapi import Security, Depends

async def authenticate(api_key: str = Security(api_key_header)):
    if not API_KEY or api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return True

@app.post("/run")
async def Run(inputs: TopicRequest, authorized: bool = Depends(authenticate)):
    """
    Run the CrewAI pipeline with given inputs.
    """
    logger = logging.getLogger("newsreportercrew")
    try:
        async with _crew_lock:
            crew = _make_crew()
            result = crew.kickoff(inputs={"topic": inputs.topic})
        sanitized_result = html.escape(str(result))
        return {"result": sanitized_result}
    except HTTPException:
        raise
    except (asyncio.TimeoutError, asyncio.CancelledError) as e:
        logger.exception("Crew execution timed out or was cancelled")
        raise HTTPException(status_code=504, detail="Request timed out") from e
    except ValueError as e:
        logger.exception("Invalid input for crew execution")
        raise HTTPException(status_code=400, detail="Invalid input provided") from e
    except RuntimeError as e:
        logger.exception("Runtime error during crew execution")
        raise HTTPException(status_code=500, detail="Internal server error") from e
    except Exception as e:
        logger.exception("Unexpected error during crew execution")
        raise HTTPException(status_code=500, detail="Internal server error") from e
