from pydantic import BaseModel

from enums.equipment_type import EquipmentType


class DetailedExerciseLog(BaseModel):
    # exercise_log
    exercise_log_id: int
    user_id: int
    workout_day_exercise_id: int
    program_week: int
    weight: float
    sets_completed: int | None
    reps_in_reserve: int | None
    notes: str | None
    completed: bool
    # workout_day_exercises
    workout_program_id: int
    workout_day: int
    target_sets: int
    target_reps: int
    intensity: float
    optional: bool
    # exercises
    exercise_id: int
    exercise_name: str
    equipment_type: EquipmentType
    weight_increment: float
    # workout_programs
    workout_program_name: str
