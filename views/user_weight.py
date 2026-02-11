from pydantic import BaseModel


class UserWeight(BaseModel):
    id: int
    weight: float
    date: str
