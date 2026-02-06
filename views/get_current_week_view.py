from pydantic import BaseModel, ConfigDict

from enums.equipment_type import EquipmentType


# For the current day view -> specific exercise
class ExerciseEntryForDayView(BaseModel):
    model_config = ConfigDict(extra='allow')
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
    equipment_type: EquipmentType
