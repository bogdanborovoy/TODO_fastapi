from sqlmodel import create_engine


DATABASE_URL = "postgresql://user:password@db:5432/todo_db"
engine = create_engine(DATABASE_URL)
