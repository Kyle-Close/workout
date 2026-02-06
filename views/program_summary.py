from pydantic import BaseModel


class ProgramSummary(BaseModel):
    id: int
    name: str
