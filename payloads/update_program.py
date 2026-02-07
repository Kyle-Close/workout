from pydantic import BaseModel

class UpdateProgramPayload(BaseModel):
    name: str
