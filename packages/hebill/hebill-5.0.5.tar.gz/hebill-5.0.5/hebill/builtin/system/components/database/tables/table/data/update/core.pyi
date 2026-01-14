from ...__data__ import Data
from .....queries.plugins.conditions import Conditions


class Update(Data):
    @property
    def conditions(self) -> Conditions: ...

    def execute(self, data: dict) -> None: ...

