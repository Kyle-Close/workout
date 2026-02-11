from pydantic import BaseModel


class ProgramDayExercise(BaseModel):
    id: int
    exercise_name: str
    target_sets: int
    target_reps: int
    intensity: float
    optional: bool
    equipment_type: str


class ProgramDay(BaseModel):
    day: int
    exercises: list[ProgramDayExercise]


class ProgramDetail(BaseModel):
    id: int
    name: str
    days: list[ProgramDay]
