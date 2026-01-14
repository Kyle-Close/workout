from pydantic import BaseModel

class GenerateLogsWeekPayload(BaseModel):
    user_id: int
    workout_program_id: int
