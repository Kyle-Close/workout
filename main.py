import sqlite3
from collections.abc import Generator

from enums.equipment_type import EquipmentType
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from db.db import DB, DatabaseConnectionError
from helpers.plate_calculator import PlateCalculator
from payloads.create_exercise import CreateExercisePayload
from payloads.create_program import CreateProgramPayload
from payloads.generate_logs_week import GenerateLogsWeekPayload
from payloads.update_program import UpdateProgramPayload
from payloads.update_program_exercises import UpdateProgramExercisesPayload
from repositories.exercise_repository import ExerciseRepository
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

    exerciseLogs = exercise_logs_service.get_exercise_logs_by_week(user_id, workout_program_id, current_week)
    
    for log in exerciseLogs:
        if log.equipment_type == EquipmentType.BARBELL:
            pCalc = PlateCalculator(log.weight)
            log.plates = pCalc.calculate()

    return {
        "currentDayOfWeek": current_day_of_week,
        "weekData": exerciseLogs,
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


@app.get("/exercises/history")
def get_exercise_history(user_id: int, exercise_id: int, db: DB = Depends(get_db)):
    exercise_log_service = ExerciseLogService(db)
    exercise_name, history = exercise_log_service.get_exercise_history(user_id, exercise_id)
    return {
        "exercise_id": exercise_id,
        "exercise_name": exercise_name,
        "history": history,
    }


@app.get("/exercises")
def get_exercises(db: DB = Depends(get_db)):
    exercise_repo = ExerciseRepository(db)
    return exercise_repo.get_all()


@app.post("/exercises", status_code=201)
def create_exercise(payload: CreateExercisePayload, db: DB = Depends(get_db)):
    exercise_repo = ExerciseRepository(db)
    existing = exercise_repo.find_by_name(payload.name)
    if existing:
        raise HTTPException(status_code=409, detail="Exercise with this name already exists")
    exercise_id = exercise_repo.create_exercise(payload.name, payload.equipment_type, payload.weight_increment)
    return {"id": exercise_id, "name": payload.name, "equipment_type": payload.equipment_type, "weight_increment": payload.weight_increment}


@app.get("/programs")
def get_programs(user_id: int, db: DB = Depends(get_db)):
    workout_service = WorkoutService(db)
    return workout_service.get_user_programs(user_id)


@app.get("/programs/{program_id}")
def get_program_detail(program_id: int, db: DB = Depends(get_db)):
    workout_service = WorkoutService(db)
    result = workout_service.get_program_detail(program_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Program not found")
    return result

@app.post("/programs/recommended", status_code=201)
def create_recommended_program(user_id: int, db: DB = Depends(get_db)):
    workout_service = WorkoutService(db)
    return workout_service.create_recommended_program(user_id)

@app.post("/programs", status_code=201)
def create_program(payload: CreateProgramPayload, db: DB = Depends(get_db)):
    workout_service = WorkoutService(db)
    return workout_service.create_program(
        payload.user_id, payload.name, [e.model_dump() for e in payload.exercises]
    )

@app.delete("/programs/{program_id}", status_code=204)
def delete_program(program_id: int, user_id: int, db: DB = Depends(get_db)):
    workout_service = WorkoutService(db)
    workout_service.delete_program(program_id, user_id)

@app.patch("/programs/{program_id}")
def update_program(program_id: int, payload: UpdateProgramPayload, db: DB = Depends(get_db)):
    workout_service = WorkoutService(db)
    return workout_service.update_program(program_id, payload.name)

@app.patch("/programs/{program_id}/exercises")
def update_program_exercises(program_id: int, payload: UpdateProgramExercisesPayload, db: DB = Depends(get_db)):
    workout_service = WorkoutService(db)
    result = workout_service.update_program_exercises(
        program_id, [e.model_dump() for e in payload.exercises]
    )
    if result is None:
        raise HTTPException(status_code=404, detail="Program not found")
    return result
