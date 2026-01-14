from .number import Number
from ..he import He


class Hf(He, float, Number):
    def __new__(cls, u: He, number: str | float | int): ...
    def __init__(self, u: He, number: str | float | int): ...
