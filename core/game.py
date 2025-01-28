from dataclasses import dataclass


@dataclass
class Game:
    width: int
    height: int
    bombs: int


beginner = Game(9, 9, 10)
beginner_new = Game(10, 10, 10)
intermediate = Game(16, 16, 40)
expert = Game(30, 16, 99)
