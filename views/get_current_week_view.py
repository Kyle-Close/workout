from pydantic import BaseModel


# For the current day view -> specific exercise
class ExerciseEntryForDayView(BaseModel):
    exercise_log_id: int
    exercise_name: str
    program_week: int
    workout_day: int
    weight: int
    target_sets: int
    target_reps: int
    sets_completed: int | None
    reps_in_reserve: int | None
    optional: bool
    workout_day_exercise_id: int
    completed: bool
