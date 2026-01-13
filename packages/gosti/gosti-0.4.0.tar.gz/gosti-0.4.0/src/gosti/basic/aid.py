import math
from typing import Union

Number = Union[int, float]


def hypot2(a: float, b: float) -> float:
    return math.sqrt(a * a + b * b)

def hypot3(a: float, b: float, c: float) -> float:
    return math.sqrt(a * a + b * b + c * c)
