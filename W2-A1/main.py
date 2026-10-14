from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class Task(BaseModel):
    id: int
    title: str
    done: bool = False

class TaskCreate(BaseModel):
    title: str

class TaskUpdate(BaseModel):
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

@app.post("/tasks")
async def create_task(task: TaskCreate):
    if not task.title:
        raise HTTPException(status_code=400, detail={ "error": "Task title is required" })
    new_id = max(task.id for task in tasks) + 1
    new_task = Task(id=new_id, title=task.title)
    tasks.append(new_task)
    return new_task

@app.put("/tasks/{id}")
async def update_task(id: int, task: TaskUpdate):
    existing_task = next((task for task in tasks if task.id == id), None)
    if existing_task is None:
        raise HTTPException(status_code=404, detail={ "error": f"Task {id} not found" })
    if not task.title:
        raise HTTPException(status_code=400, detail={ "error": "Task title is required" })
    existing_task.title = task.title
    existing_task.done = task.done
    return existing_task

@app.delete("/tasks/{id}")
async def delete_task(id: int):
    existing_task = next((task for task in tasks if task.id == id), None)
    if existing_task is None:
        raise HTTPException(status_code=404, detail={ "error": f"Task {id} not found" })
    tasks.remove(existing_task)
    return {"message": f"Task {id} deleted successfully"}

