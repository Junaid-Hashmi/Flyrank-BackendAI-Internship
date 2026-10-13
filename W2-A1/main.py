from fastapi import FastAPI, HTTPException

app = FastAPI()

tasks = [
    {"id": 1, "title": "Task 1", "completed": False},
    {"id": 2, "title": "Task 2", "completed": True},
    {"id": 3, "title": "Task 3", "completed": False}
]

@app.get("/")
async def read_root():
    return {"name": "Task API", "version": "1.0", "endpoint": ["/tasks"]}

@app.get("/health")
async def health_check():
    return {"status": "ok"}