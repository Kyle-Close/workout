from fastapi import FastAPI
from Exercise import Exercise
from enums.muscle_group import MuscleGroup
from enums.equipment_type import EquipmentType

app = FastAPI()


@app.get("/")
async def root():
    squat = Exercise(
        "Squat",
        [MuscleGroup.GLUTES, MuscleGroup.QUADS, MuscleGroup.HAMSTRINGS],
        EquipmentType.BARBELL,
    )
    return {"Exercise": squat}
