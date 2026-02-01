from pydantic import BaseModel


class CompleteDayCalcOneRepMaxView(BaseModel):
    user_id: int
    exercise_id: int
    current_one_rep_max: float
    target_sets: int
    sets_completed: int
    reps_in_reserve: int
    workout_day: int
    workout_program_id: int
    workout_day_exercise_id: int
    exercise_name: str

