from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os

from lifeledger_agent import run_agent, notifications, store

app = FastAPI(title="LifeLedger API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/api/notifications")
async def get_notifications():
    return JSONResponse(content={"notifications": notifications[::-1]})

@app.post("/api/simulate")
async def simulate(payload: dict):
    text = payload.get("text", "")
    run_agent(text)
    return {"status": "success", "message": "Agent processed the input"}

@app.post("/api/decision")
async def decision(payload: dict):
    task_id = payload.get("task_id")
    outcome = payload.get("outcome")
    feedback = payload.get("feedback", "")
    
    store.log_decision(task_id, outcome, feedback)
    
    for n in notifications:
        if n["task_id"] == task_id:
            n["status"] = outcome
            break
            
    return {"status": "success"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
