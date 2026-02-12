import sqlite3
from collections.abc import Generator

from enums.equipment_type import EquipmentType
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from auth.auth import (
    TokenData,
    create_access_token,
    get_current_user,
    hash_password,
    require_admin,
    verify_password,
)
from db.db import DB, DatabaseConnectionError
from helpers.plate_calculator import PlateCalculator
from payloads.create_exercise import CreateExercisePayload
from payloads.create_program import CreateProgramPayload
from payloads.create_user_weight import CreateUserWeightPayload
from payloads.generate_logs_week import GenerateLogsWeekPayload
from payloads.set_one_rep_max import SetOneRepMaxPayload
from payloads.login import LoginPayload
from payloads.register import RegisterPayload
from payloads.update_program import UpdateProgramPayload
from payloads.update_program_exercises import UpdateProgramExercisesPayload
from repositories.exercise_repository import ExerciseRepository
from repositories.one_rep_max_repository import OneRepMaxRepository
from repositories.user_repository import UserRepository
from services.demo_service import DemoService
from services.exercise_log_service import ExerciseLogService
from services.one_rep_max_service import OneRepMaxService
from services.workout_service import WorkoutService
from views.exercise_log import ExerciseLog
from views.user_weight import UserWeight

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


# ---------- Auth endpoints (no token required) ----------


@app.post("/register", status_code=201)
def register(payload: RegisterPayload, db: DB = Depends(get_db)):
    user_repo = UserRepository(db)
    existing = user_repo.get_user_by_username(payload.username)
    if existing:
        raise HTTPException(status_code=409, detail="Username already taken")
    password_hash = hash_password(payload.password)
    user_id = user_repo.create_user(payload.username, password_hash)
    token = create_access_token(user_id, payload.username, "user")
    return {"access_token": token, "token_type": "bearer"}


@app.post("/demo-login")
def demo_login(db: DB = Depends(get_db)):
    demo_service = DemoService(db)
    user_id, username = demo_service.reset_and_seed()
    token = create_access_token(user_id, username, "demo")
    return {"access_token": token, "token_type": "bearer"}


@app.post("/login")
def login(payload: LoginPayload, db: DB = Depends(get_db)):
    user_repo = UserRepository(db)
    user = user_repo.get_user_by_username(payload.username)
    if not user or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(user["id"], user["username"], user["role"])
    return {"access_token": token, "token_type": "bearer"}


# ---------- Protected endpoints ----------


@app.get("/get-current-week-data")
def get_current_week_data(
    workout_program_id: int,
    db: DB = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    user_id = current_user.user_id
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
def generate_logs_week_endpoint(
    payload: GenerateLogsWeekPayload,
    db: DB = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    workout_service = WorkoutService(db)
    workout_service.populate_exercise_logs_week(current_user.user_id, payload.workout_program_id)
    return "Successfully generated a weeks worth of exercise logs for program"


@app.patch("/update-logs")
def update_logs_endpoint(
    payload: list[ExerciseLog],
    db: DB = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    if not payload:
        raise HTTPException(status_code=400, detail="No exercise logs provided")

    for log in payload:
        log.user_id = current_user.user_id

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
def get_one_rep_maxes(
    db: DB = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    one_rep_max_service = OneRepMaxService(db)
    return one_rep_max_service.user_one_rep_max_data(current_user.user_id)


@app.put("/one-rep-maxes")
def set_one_rep_maxes(
    payload: SetOneRepMaxPayload,
    db: DB = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    one_rep_max_repo = OneRepMaxRepository(db)
    for entry in payload.maxes:
        one_rep_max_repo.upsert_one_rep_max(current_user.user_id, entry.exercise_id, entry.one_rep_max)
    one_rep_max_service = OneRepMaxService(db)
    return one_rep_max_service.user_one_rep_max_data(current_user.user_id)


@app.get("/active-week")
def get_active_week(
    workout_program_id: int,
    db: DB = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    workout_service = WorkoutService(db)
    current_week = workout_service.get_latest_program_week_entry(current_user.user_id, workout_program_id)
    return current_week


@app.get("/week-logs")
def get_week_logs(
    workout_program_id: int,
    week_num: int,
    db: DB = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    exercise_log_service = ExerciseLogService(db)
    return exercise_log_service.get_exercise_logs_by_week(current_user.user_id, workout_program_id, week_num)


@app.get("/exercises/history")
def get_exercise_history(
    exercise_id: int,
    db: DB = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    exercise_log_service = ExerciseLogService(db)
    exercise_name, history = exercise_log_service.get_exercise_history(current_user.user_id, exercise_id)
    return {
        "exercise_id": exercise_id,
        "exercise_name": exercise_name,
        "history": history,
    }


@app.get("/exercises")
def get_exercises(
    db: DB = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    exercise_repo = ExerciseRepository(db)
    return exercise_repo.get_all()


@app.post("/exercises", status_code=201)
def create_exercise(
    payload: CreateExercisePayload,
    db: DB = Depends(get_db),
    current_user: TokenData = Depends(require_admin),
):
    exercise_repo = ExerciseRepository(db)
    existing = exercise_repo.find_by_name(payload.name)
    if existing:
        raise HTTPException(status_code=409, detail="Exercise with this name already exists")
    exercise_id = exercise_repo.create_exercise(payload.name, payload.equipment_type, payload.weight_increment)
    return {"id": exercise_id, "name": payload.name, "equipment_type": payload.equipment_type, "weight_increment": payload.weight_increment}


@app.get("/programs")
def get_programs(
    db: DB = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    workout_service = WorkoutService(db)
    return workout_service.get_user_programs(current_user.user_id)


@app.get("/programs/{program_id}")
def get_program_detail(
    program_id: int,
    db: DB = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    workout_service = WorkoutService(db)
    result = workout_service.get_program_detail(program_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Program not found")
    return result


@app.post("/programs/recommended", status_code=201)
def create_recommended_program(
    db: DB = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    workout_service = WorkoutService(db)
    return workout_service.create_recommended_program(current_user.user_id)


@app.post("/programs", status_code=201)
def create_program(
    payload: CreateProgramPayload,
    db: DB = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    workout_service = WorkoutService(db)
    return workout_service.create_program(
        current_user.user_id, payload.name, [e.model_dump() for e in payload.exercises]
    )


@app.delete("/programs/{program_id}", status_code=204)
def delete_program(
    program_id: int,
    db: DB = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    workout_service = WorkoutService(db)
    workout_service.delete_program(program_id, current_user.user_id)


@app.patch("/programs/{program_id}")
def update_program(
    program_id: int,
    payload: UpdateProgramPayload,
    db: DB = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    workout_service = WorkoutService(db)
    return workout_service.update_program(program_id, payload.name)


@app.patch("/programs/{program_id}/exercises")
def update_program_exercises(
    program_id: int,
    payload: UpdateProgramExercisesPayload,
    db: DB = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    workout_service = WorkoutService(db)
    result = workout_service.update_program_exercises(
        program_id, [e.model_dump() for e in payload.exercises]
    )
    if result is None:
        raise HTTPException(status_code=404, detail="Program not found")
    return result


@app.post("/user-weight", status_code=201, response_model=UserWeight)
def create_user_weight(
    payload: CreateUserWeightPayload,
    db: DB = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    user_repo = UserRepository(db)
    weight_id = user_repo.create_user_weight(current_user.user_id, payload.weight, payload.date)
    return UserWeight(id=weight_id, weight=payload.weight, date=payload.date)


@app.get("/user-weight", response_model=list[UserWeight])
def get_user_weight_history(
    db: DB = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    user_repo = UserRepository(db)
    return user_repo.get_user_weight_history(current_user.user_id)


@app.delete("/user-weight/{weight_id}", status_code=204)
def delete_user_weight(
    weight_id: int,
    db: DB = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    user_repo = UserRepository(db)
    deleted = user_repo.delete_user_weight(weight_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Weight entry not found")
