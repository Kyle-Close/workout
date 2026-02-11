from pydantic import BaseModel


class CreateUserWeightPayload(BaseModel):
    user_id: int
    weight: float
    date: str
