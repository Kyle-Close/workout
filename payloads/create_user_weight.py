from pydantic import BaseModel


class CreateUserWeightPayload(BaseModel):
    weight: float
    date: str
