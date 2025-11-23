from sqlmodel import SQLModel, Field


class TaskBase(SQLModel):
    name: str
    time_limit: str


class Task(TaskBase, table=True):
    id: int | None = Field(default=None, primary_key=True)


class TaskRead(TaskBase):
    id: int


class TaskUpdate(SQLModel):
    name: str | None = None
    time_limit: str | None = None


class TaskCreate(TaskBase):
    pass

