from pydantic import BaseModel


class ExerciseLog(BaseModel):
    id: int
    user_id: int
    workout_day_exercise_id: int
    program_week: int
    weight: int
    sets_completed: int
    reps_in_reserve: int
    notes: str
    completed: bool
