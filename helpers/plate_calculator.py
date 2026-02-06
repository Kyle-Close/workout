from dataclasses import dataclass

@dataclass
class PlateBreakdown:
    plates_45: int
    plates_35: int
    plates_25: int
    plates_10: int
    plates_5: int
    plates_2_5: int 

class PlateCalculator:
    def __init__(self, total_weight: float) -> None:
        self.bar_weight = 45
        self.total_weight = total_weight

    def calculate(self) -> PlateBreakdown:
        weight_to_load = (self.total_weight - self.bar_weight) / 2  # Per side

        plates_45 = int(weight_to_load // 45)
        weight_to_load %= 45

        plates_35 = int(weight_to_load // 35)
        weight_to_load %= 35

        plates_25 = int(weight_to_load // 25)
        weight_to_load %= 25

        plates_10 = int(weight_to_load // 10)
        weight_to_load %= 10

        plates_5 = int(weight_to_load // 5)
        weight_to_load %= 5

        plates_2_5 = int(weight_to_load // 2.5)

        return PlateBreakdown(
            plates_45=plates_45,
            plates_35=plates_35,
            plates_25=plates_25,
            plates_10=plates_10,
            plates_5=plates_5,
            plates_2_5=plates_2_5
        )
