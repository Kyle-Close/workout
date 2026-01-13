from collections.abc import Generator
from fastapi import Depends, FastAPI
from core.PopulateExerciseLogsWeek import populate_exercise_logs_week
from db.db import DB

app = FastAPI()


def get_db() -> Generator[DB, None, None]:
    db = DB()
    try:
        yield db
        db.connection.commit()
    except Exception:
        db.connection.rollback()
        raise
    finally:
        db.close()


@app.get("/")
def root(db: DB = Depends(get_db)):
    populate_exercise_logs_week(db, 1, 1)
