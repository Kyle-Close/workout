from pydantic import BaseModel


class UserOneRepMaxWithExercise(BaseModel):
    exercise_id: int
    name: str
    weight_increment: float
    original_one_rep_max: float
    current_one_rep_max: float

