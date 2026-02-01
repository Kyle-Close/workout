from pydantic import BaseModel


class UserOneRepMaxWithName(BaseModel):
    id: int
    user_id: int
    exercise_id: int
    exercise_name: str
    original_one_rep_max: float
    current_one_rep_max: float
