from enums.equipment_type import EquipmentType
from enums.muscle_group import MuscleGroup


class Exercise:
    name: str
    target_muscles: list[MuscleGroup]
    equipment_type: EquipmentType

    def __init__(
        self,
        name: str,
        target_muscles: list[MuscleGroup],
        equipment_type: EquipmentType,
    ):
        self.name = name
        self.target_muscles = target_muscles
        self.equipment_type = equipment_type
