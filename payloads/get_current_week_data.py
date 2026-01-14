from pydantic import BaseModel


class GetCurrentWeekDataPayload(BaseModel):
    user_id: int
    workout_program_id: int
