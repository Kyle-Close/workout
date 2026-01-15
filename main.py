from collections.abc import Generator
from fastapi import Depends, FastAPI
from core.CalculateNewOneRepMax import calculate_new_one_rep_max
from core.CompleteDay import complete_day_logs
from core.PopulateExerciseLogsWeek import populate_exercise_logs_week
from db.db import DB
from db.selects import (
    get_latest_program_week_entry,
    get_number_of_days_in_program_week,
    get_complete_day_calc_one_rep_max_query_res,
    get_user_program_exercise_logs_by_week,
)
from db.updates import update_one_rep_max
from payloads.generate_logs_week import GenerateLogsWeekPayload
from views.exercise_log import ExerciseLog
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
)

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


@app.get("/get-current-week-data")
def get_current_week_data(user_id: int, workout_program_id: int, db: DB = Depends(get_db)):
    current_week = get_latest_program_week_entry(db, user_id, workout_program_id)
    return get_user_program_exercise_logs_by_week(db, user_id, workout_program_id, current_week)


@app.post("/generate-logs-week")
def generate_logs_week_endpoint(
    payload: GenerateLogsWeekPayload, db: DB = Depends(get_db)
):
    populate_exercise_logs_week(db, payload.user_id, payload.workout_program_id)
    return "Successfully generated a weeks worth of exercise logs for program"


@app.patch("/complete-day")
def complete_day_endpoint(payload: list[ExerciseLog], db: DB = Depends(get_db)):
    workout_day = -1
    workout_program_id = -1
    user_id = -1
    msg = ""

    # 1. Update the exercise log entries with sets, rip, notes, and mark as complete
    complete_day_logs(db, payload)

    # 2. For each completed exercise, calculate a new 1 rep max
    result = get_complete_day_calc_one_rep_max_query_res(
        db, payload[0].user_id, [log.workout_day_exercise_id for log in payload]
    )

    for i in result:
        workout_day = i.workout_day
        workout_program_id = i.workout_program_id
        user_id = i.user_id
        idx = next(
            idx
            for idx, log in enumerate(payload)
            if log.workout_day_exercise_id == i.workout_day_exercise_id
        )
        sets_completed = payload[idx].sets_completed
        rir = payload[idx].reps_in_reserve

        if sets_completed is None or rir is None:
            continue

        max = calculate_new_one_rep_max(
            i.one_rep_max,
            sets_completed - i.target_sets,
            rir,
        )
        update_one_rep_max(db, i.user_id, i.exercise_id, max)

    msg += f"Successfully updated {len(payload)} logs!"

    # 3. Check if we just completed the final day of the week. If we did, we need to generate a new week of logs
    final_day = get_number_of_days_in_program_week(db, workout_program_id)

    if workout_day == final_day:
        populate_exercise_logs_week(db, user_id, workout_program_id)
        msg += "\nWeek completed! Generated next weeks exercise logs."

    return msg
