from pydantic import BaseModel


class GenerateLogsWeekPayload(BaseModel):
    workout_program_id: int
