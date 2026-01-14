from ..he import He
from ..hf.number import Number


class Hi(He, int, Number):
    def __new__(cls, u: He, number: str | float | int): ...
    def __init__(self, u: He, number: str | float | int): ...
