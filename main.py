from collections.abc import Generator

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from db.db import DB
from payloads.generate_logs_week import GenerateLogsWeekPayload
from services.workout_service import WorkoutService
from services.one_rep_max_service import OneRepMaxService
from services.exercise_log_service import ExerciseLogService
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
    exercise_log_service = ExerciseLogService(db)

    # 1. Update exercise logs with payload data
    workout_service.update_exercise_logs(payload)

    # 2. Update user 1 rep maxes based on the updated logs
    one_rep_max_updates = one_rep_max_service.update_maxes_from_completed_logs(payload)

    # 3. Check if we need to generate a new week of logs
    first_log_detailed = exercise_log_service.get_detailed_log_info([payload[0].id])
    details = first_log_detailed[0]

    latest_week = workout_service.get_latest_program_week_entry(details.user_id, details.workout_program_id)

    should_populate_new_week = workout_service.check_is_week_complete(
        details.user_id, details.workout_program_id, latest_week
    )

    if should_populate_new_week:
        workout_service.populate_exercise_logs_week(details.user_id, details.workout_program_id)

    return {
        "logs_updated": len(one_rep_max_updates),
        "maxes_updated": one_rep_max_updates,
        "generated_new_week": should_populate_new_week,
        "message": f"Successfully updated {len(payload)} exercise log(s) and {len(one_rep_max_updates)} one rep max(es).",
    }
