from collections.abc import Generator
from venv import logger

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from db.db import DB
from db.selects import (
    get_exercise_data_for_updating_maxes,
    get_current_workout_day_of_week,
    get_latest_program_week_entry,
    get_number_of_days_in_program_week,
    get_user_program_exercise_logs_by_week,
)
from db.updates import update_many_exercise_logs, update_one_rep_max
from payloads.generate_logs_week import GenerateLogsWeekPayload
from services import workout_service
from services.workout_service import WorkoutService
from services.one_rep_max_service import OneRepMaxService
from views.exercise_log import ExerciseLog

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
def get_current_week_data(
    user_id: int, workout_program_id: int, db: DB = Depends(get_db)
):
    current_week = get_latest_program_week_entry(db, user_id, workout_program_id)
    data = get_user_program_exercise_logs_by_week(
        db, user_id, workout_program_id, current_week
    )
    current_day_of_week = get_current_workout_day_of_week(
        db, user_id, workout_program_id, current_week
    )

    return {
        "currentDayOfWeek": current_day_of_week,
        "weekData": data,
    }


@app.post("/generate-logs-week")
def generate_logs_week_endpoint(
    payload: GenerateLogsWeekPayload, db: DB = Depends(get_db)
):
    workout_service = WorkoutService(db)
    workout_service.populate_exercise_logs_week(
        payload.user_id, payload.workout_program_id
    )
    return "Successfully generated a weeks worth of exercise logs for program"


@app.patch("/update-logs")
def update_logs_endpoint(payload: list[ExerciseLog], db: DB = Depends(get_db)):
    if not payload:
        raise HTTPException(status_code=400, detail="No exercise logs provided")

    workout_service = WorkoutService(db)
    workout_service.update_exercise_logs(payload)

    one_rep_max_service = OneRepMaxService(db)
    one_rep_max_updates = one_rep_max_service.update_maxes_from_completed_logs(payload)

    # 3. Check if we just completed the final day of the week. If we did, we need to generate a new week of logs
    # TODO

    return {
        "logs_updated": len(one_rep_max_updates),
        "maxes_updated": one_rep_max_updates,
        "week_completed": False,  # TODO - for now, hard-coding
        "message": f"Successfully updated {len(payload)} exercise log(s) and {len(one_rep_max_updates)} one rep max(es). Week completed! Generated next week's exercise logs.",
    }
