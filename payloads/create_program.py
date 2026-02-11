from pydantic import BaseModel


class CreateProgramExercise(BaseModel):
    exercise_id: int
    workout_day: int
    target_sets: int
    target_reps: int
    intensity: float
    optional: bool = False


class CreateProgramPayload(BaseModel):
    name: str
    exercises: list[CreateProgramExercise]
