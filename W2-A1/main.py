from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class Task(BaseModel):
    id: int
    title: str
    done: bool

tasks = [
    Task(id=1, title="Task 1", done=False),
    Task(id=2, title="Task 2", done=True),
    Task(id=3, title="Task 3", done=False)
]

@app.get("/")
async def read_root():
    return {"name": "Task API", "version": "1.0", "endpoint": ["/tasks"]}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/tasks")
async def get_tasks():
    return tasks

@app.get("/tasks/{id}")
async def get_task(id: int):
    task = next((task for task in tasks if task.id == id), None)
    if task is None:
        raise HTTPException(status_code=404, detail={ "error": f"Task {id} not found" })
    return task