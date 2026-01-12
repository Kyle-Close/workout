from typing import override


class User:
    id: int
    username: str

    def __init__(self, cursorResult: tuple[int, str]):
        self.id = cursorResult[0]
        self.username = cursorResult[1]

    @override
    def __str__(self) -> str:
        return f"id: {self.id}\nusername: {self.username}\n"
