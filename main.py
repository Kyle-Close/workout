from fastapi import FastAPI
from core.PopulateExerciseLogsWeek import populate_exercise_logs_week
from enums.equipment_type import EquipmentType
from db.db import db

app = FastAPI()
db = db()
populate_exercise_logs_week(db, 1, 1)


@app.get("/")
async def root():
    pass
