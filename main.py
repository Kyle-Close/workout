import sqlite3
from collections.abc import Generator

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from db.db import DB, DatabaseConnectionError
from payloads.generate_logs_week import GenerateLogsWeekPayload
from services.exercise_log_service import ExerciseLogService
from services.one_rep_max_service import OneRepMaxService
from services.workout_service import WorkoutService
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
    try:
        db = DB()
    except DatabaseConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e

    try:
        yield db
        db.connection.commit()
    except sqlite3.Error:
        db.connection.rollback()
        raise
    finally:
        db.close()


@app.get("/get-current-week-data")
def get_current_week_data(user_id: int, workout_program_id: int, db: DB = Depends(get_db)):
    workout_service = WorkoutService(db)
    exercise_logs_service = ExerciseLogService(db)

    current_week = workout_service.get_latest_program_week_entry(user_id, workout_program_id)
    current_day_of_week = exercise_logs_service.get_current_day_of_week(user_id, workout_program_id, current_week)

    data = exercise_logs_service.get_exercise_logs_by_week(user_id, workout_program_id, current_week)

    return {
        "currentDayOfWeek": current_day_of_week,
        "weekData": data,
    }


@app.post("/generate-logs-week")
def generate_logs_week_endpoint(payload: GenerateLogsWeekPayload, db: DB = Depends(get_db)):
    workout_service = WorkoutService(db)
    workout_service.populate_exercise_logs_week(payload.user_id, payload.workout_program_id)
    return "Successfully generated a weeks worth of exercise logs for program"


@app.patch("/update-logs")
def update_logs_endpoint(payload: list[ExerciseLog], db: DB = Depends(get_db)):
    if not payload:
        raise HTTPException(status_code=400, detail="No exercise logs provided")

    workout_service = WorkoutService(db)
    one_rep_max_service = OneRepMaxService(db)

    result = workout_service.process_log_updates(payload, one_rep_max_service)

    return {
        "logs_updated": result.logs_updated,
        "maxes_updated": result.maxes_updated,
        "generated_new_week": result.generated_new_week,
        "message": f"Successfully updated {result.logs_updated} exercise log(s) and {len(result.maxes_updated)} one rep max(es).",
    }


@app.get("/one-rep-maxes")
def get_one_rep_maxes(user_id: int, db: DB = Depends(get_db)):
    one_rep_max_service = OneRepMaxService(db)
    return one_rep_max_service.user_one_rep_max_data(user_id)


@app.get("/active-week")
def get_active_week(user_id: int, workout_program_id: int, db: DB = Depends(get_db)):
    workout_service = WorkoutService(db)
    current_week = workout_service.get_latest_program_week_entry(user_id, workout_program_id)
    return current_week


@app.get("/week-logs")
def get_active_week(user_id: int, workout_program_id: int, week_num: int, db: DB = Depends(get_db)):
    exercise_log_service = ExerciseLogService(db)
    return exercise_log_service.get_exercise_logs_by_week(user_id, workout_program_id, week_num)
