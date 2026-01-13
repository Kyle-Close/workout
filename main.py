from collections.abc import Generator
from operator import index
from fastapi import Depends, FastAPI
from core.CalculateNewOneRepMax import calculate_new_one_rep_max
from core.CompleteDay import complete_day_logs
from core.PopulateExerciseLogsWeek import populate_exercise_logs_week
from db.db import DB
from db.selects import (
    get_many_user_one_rep_maxes,
    get_user_one_rep_maxes_with_exercise_data,
    get_complete_day_calc_one_rep_max_query_res,
)
from db.updates import update_one_rep_max
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
    result = get_complete_day_calc_one_rep_max_query_res(
        db, payload[0].user_id, [log.workout_day_exercise_id for log in payload]
    )

    for i in result:
        max = calculate_new_one_rep_max(
            i.one_rep_max, i.sets_completed - i.target_sets, i.reps_in_reserve
        )
        update_one_rep_max(db, i.user_id, i.exercise_id, max)

    # 3. Check if we just completed the final day of the week. If we did, we need to generate a new week of logs
    # TODO

    return f"Successfully updated {len(payload)} logs!"
