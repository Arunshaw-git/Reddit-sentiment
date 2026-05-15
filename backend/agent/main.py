from fastapi import FastAPI, BackgroundTasks
from scrapingAndSentiment import run_agent
import os
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

load_dotenv()

app = FastAPI(title="Reddit Sentiment Agent Service")
scheduler = BackgroundScheduler()

# Schedule the agent to run every day at midnight (00:00)
scheduler.add_job(
    run_agent, 
    CronTrigger(hour=0, minute=0), 
    id="daily_agent_run",
    name="Daily Reddit Scraping and Sentiment Analysis",
    replace_existing=True
)

@app.on_event("startup")
def start_scheduler():
    scheduler.start()

@app.on_event("shutdown")
def stop_scheduler():
    scheduler.shutdown()

@app.get("/")
def read_root():
    return {
        "message": "Reddit Sentiment Agent is running",
        "next_run": str(scheduler.get_job("daily_agent_run").next_run_time)
    }

@app.post("/run")
def trigger_agent(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_agent)
    return {"message": "Agent task started in background manually"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("AGENT_PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
