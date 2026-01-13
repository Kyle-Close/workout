from collections.abc import Generator
from fastapi import Depends, FastAPI
from core.CompleteDay import complete_day_logs
from core.PopulateExerciseLogsWeek import populate_exercise_logs_week
from db.db import DB
from views.exercise_log import ExerciseLog

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
    pass


@app.patch("/complete-day")
def complete_day_endpoint(payload: list[ExerciseLog], db: DB = Depends(get_db)):
    # 1. Update the exercise log entries with sets, rip, notes, and mark as complete
    complete_day_logs(db, payload)

    # 2. For each completed exercise, calculate a new 1 rep max
    # TODO

    # 3. Check if we just completed the final day of the week. If we did, we need to generate a new week of logs
    # TODO

    return f"Successfully updated {len(payload)} logs!"
