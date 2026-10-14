from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

app = FastAPI(title="Task API", version="1.0")


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------
class Task(BaseModel):
    id: int
    title: str
    done: bool = False


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, description="Title of the task")


class TaskUpdate(BaseModel):
    title: str = Field(..., min_length=1, description="Title of the task")
    done: bool


# ---------------------------------------------------------------------------
# In-memory storage seeded with 3 dummy tasks
# ---------------------------------------------------------------------------
tasks: list[Task] = [
    Task(id=1, title="Buy groceries", done=False),
    Task(id=2, title="Write unit tests", done=True),
    Task(id=3, title="Read a book", done=False),
]


# ---------------------------------------------------------------------------
# Exception handlers
# ---------------------------------------------------------------------------
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Return a 422 with a clean error payload when the body/path is invalid."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation error",
            "detail": exc.errors(),
        },
    )


@app.exception_handler(405)
async def method_not_allowed_handler(request: Request, exc: HTTPException):
    """Return a 405 when an unsupported HTTP method is used on a route."""
    return JSONResponse(
        status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
        content={"error": f"Method {request.method} not allowed for {request.url.path}"},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """Catch-all handler so unexpected errors return a 500 instead of crashing."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "Internal server error", "detail": str(exc)},
    )


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------
def find_task(task_id: int) -> Task:
    for task in tasks:
        if task.id == task_id:
            return task
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={"error": f"Task {task_id} not found"},
    )


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.get("/")
async def read_root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.get("/tasks")
async def get_tasks():
    if not tasks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "No tasks found"},
        )
    return tasks


@app.get("/tasks/{task_id}")
async def get_task(task_id: int):
    return find_task(task_id)


@app.post("/tasks", status_code=status.HTTP_201_CREATED)
async def create_task(task: TaskCreate):
    # Reject empty titles explicitly (in addition to the Pydantic min_length).
    if not task.title.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Task title cannot be blank"},
        )

    # Prevent duplicate titles (case-insensitive) -> 409 Conflict.
    if any(existing.title.strip().lower() == task.title.strip().lower() for existing in tasks):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error": f"Task with title '{task.title}' already exists"},
        )

    new_id = max((t.id for t in tasks), default=0) + 1
    new_task = Task(id=new_id, title=task.title.strip())
    tasks.append(new_task)
    return new_task


@app.put("/tasks/{task_id}")
async def update_task(task_id: int, task: TaskUpdate):
    if not task.title.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Task title cannot be blank"},
        )

    existing_task = find_task(task_id)
    existing_task.title = task.title.strip()
    existing_task.done = task.done
    return existing_task


@app.delete("/tasks/{task_id}", status_code=status.HTTP_200_OK)
async def delete_task(task_id: int):
    existing_task = find_task(task_id)
    tasks.remove(existing_task)
    return {"message": f"Task {task_id} deleted successfully"}

