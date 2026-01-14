from decimal import Decimal
from ..hf.number import Number
from ..he import He


class Hm(He, Decimal, Number):
    def __new__(cls, u: He, number: str | float | int): ...
    def __init__(self, u: He, number: str | float | int): ...
