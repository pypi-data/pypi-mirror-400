from ...__data__ import Data
from .....queries.plugins.conditions import Conditions


class Quantity(Data):
    @property
    def conditions(self) -> Conditions: ...

    def execute(self) -> None: ...

