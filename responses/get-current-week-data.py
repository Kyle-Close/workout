from pydantic import BaseModel
from views.exercise_log import ExerciseLog


class GetCurrentWeekDataResponse(BaseModel):
    current_day: int
    day_logs: list[list[ExerciseLog]]
