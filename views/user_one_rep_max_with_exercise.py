from pydantic import BaseModel

class UserOneRepMaxWithExercise(BaseModel):
    exercise_id: int
    name: str
    weight_increment: float
    one_rep_max: float