from pydantic import BaseModel

from enums.equipment_type import EquipmentType


class CreateExercisePayload(BaseModel):
    name: str
    equipment_type: EquipmentType
    weight_increment: float
