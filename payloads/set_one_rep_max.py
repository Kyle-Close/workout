from pydantic import BaseModel


class OneRepMaxEntry(BaseModel):
    exercise_id: int
    one_rep_max: float


class SetOneRepMaxPayload(BaseModel):
    maxes: list[OneRepMaxEntry]
