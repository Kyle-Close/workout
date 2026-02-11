from pydantic import BaseModel


class ExerciseLog(BaseModel):
    id: int
    user_id: int | None = None
    workout_day_exercise_id: int
    program_week: int
    weight: float
    sets_completed: int | None
    reps_in_reserve: int | None
    notes: str | None
    completed: bool
