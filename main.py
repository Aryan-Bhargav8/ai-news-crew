from crewai import Crew, Process
from agents import researcher, reporting_analyst
from tasks import reporting_task, research_task


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

class TopicRequest(BaseModel):
    topic: str

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
        raise HTTPException(status_code=500, detail=str(e))
