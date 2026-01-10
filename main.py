from fastapi import FastAPI
from Exercise import Exercise
from enums.muscle_group import MuscleGroup
from enums.equipment_type import EquipmentType
from db.db import db

app = FastAPI()
db = db()
id = db.create_exercise("Bench Press", EquipmentType.BARBELL, 5)


@app.get("/")
async def root():
    squat = Exercise(
        "Squat",
        [MuscleGroup.GLUTES, MuscleGroup.QUADS, MuscleGroup.HAMSTRINGS],
        EquipmentType.BARBELL,
    )
    return {"Exercise": squat}
