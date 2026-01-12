from fastapi import FastAPI
from Exercise import Exercise
from enums.muscle_group import MuscleGroup
from enums.equipment_type import EquipmentType
from db.db import db

app = FastAPI()
db = db()
print(db.get_program_workout_days_excercises_data(1))

def calculate_new_one_rep_max(current_one_rep_max: int, set_delta: int, rip: int):
    # set delta = amount of sets completed vs target. -2 would mean just 1 set completed if target is 3
    # rip = reps in reserve on last set
    percent_to_add = 0

    if set_delta == -1:
        percent_to_add = -0.02
    elif set_delta < -1:
        percent_to_add = -0.05
    elif rip == 1:
        percent_to_add = 0.01
    elif rip == 2:
        percent_to_add = 0.03
    elif rip > 2:
        percent_to_add = 0.05
    return current_one_rep_max * (1 + percent_to_add)

print(calculate_new_one_rep_max(100, 0, 3))

@app.get("/")
async def root():
    squat = Exercise(
        "Squat",
        [MuscleGroup.GLUTES, MuscleGroup.QUADS, MuscleGroup.HAMSTRINGS],
        EquipmentType.BARBELL,
    )
    return {"Exercise": squat}
