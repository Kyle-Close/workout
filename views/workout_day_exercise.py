from pydantic import BaseModel

class WorkoutDayExercise(BaseModel):
    id: int
    exercise_id: int
    program_id: int
    workout_day: int
    target_sets: int
    target_reps: int
    intensity: float
    exercise_name: str
