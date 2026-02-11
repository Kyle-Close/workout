from pydantic import BaseModel


class UpdateProgramExercise(BaseModel):
    id: int
    target_sets: int
    target_reps: int
    intensity: float


class UpdateProgramExercisesPayload(BaseModel):
    exercises: list[UpdateProgramExercise]
