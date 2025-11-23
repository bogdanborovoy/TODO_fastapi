import json
from typing import Annotated

from contextlib import asynccontextmanager
from fastapi import FastAPI, Path, HTTPException, status, Response, Depends
from sqlmodel import Session, SQLModel, select
from database import engine
from fastapi.middleware.cors import CORSMiddleware
from models import TaskRead, Task, TaskCreate, TaskUpdate

from celery_worker import do_nothing
from redis import Redis

redis_client = Redis(host="redis", port=6379, db=0, decode_responses=True)

def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get("/tasks/", response_model=list[TaskRead])
def read_tasks(session: SessionDep):
    cached_tasks = redis_client.get("all_tasks")
    if cached_tasks:
        return json.loads(cached_tasks)
    do_nothing.delay()
    tasks = session.exec(select(Task)).all()

    tasks_json = json.dumps([t.model_dump() for t in tasks])
    redis_client.setex("all_tasks", 30, tasks_json)
    return tasks

@app.get("/tasks/{task_id}", response_model=TaskRead)
def read_task(task_id: Annotated[int, Path()], session: SessionDep):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@app.post("/tasks/", response_model=TaskRead)
def create_task(session: SessionDep, task: TaskCreate):
    task_db = Task.model_validate(task)
    session.add(task_db)
    session.commit()
    session.refresh(task_db)
    redis_client.delete("all_tasks")
    return task_db


@app.put("/tasks/{task_id}", response_model=TaskRead)
def replace_task(task_id: Annotated[int, Path()], new_task: TaskCreate, session: SessionDep):
    task_db = session.get(Task, task_id)
    if not task_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    task_data = new_task.model_dump()
    task_db.sqlmodel_update(task_data)

    session.commit()
    session.refresh(task_db)
    redis_client.delete("all_tasks")
    return task_db


@app.patch("/tasks/{task_id}", response_model=TaskRead)
def update_task(task_id: Annotated[int, Path()], new_task: TaskUpdate, session: SessionDep):
    task_db = session.get(Task, task_id)
    if not task_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    task_data = new_task.model_dump(exclude_unset=True)
    task_db.sqlmodel_update(task_data)

    session.commit()
    session.refresh(task_db)
    redis_client.delete("all_tasks")
    return task_db


@app.delete("/tasks/{task_id}")
def delete_task(task_id: Annotated[int, Path()], session: SessionDep):
    task_db = session.get(Task, task_id)
    if not task_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    session.delete(task_db)
    session.commit()
    redis_client.delete("all_tasks")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
