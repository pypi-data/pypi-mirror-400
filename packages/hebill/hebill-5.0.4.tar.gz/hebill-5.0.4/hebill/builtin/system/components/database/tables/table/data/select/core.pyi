from ...__data__ import Data
from .....queries.plugins.columns import Columns
from .....queries.plugins.conditions import Conditions
from .....queries.plugins.limits import Limits
from .....queries.plugins.orders import Orders


class Select(Data):
    @property
    def columns(self) -> Columns: ...
    @property
    def conditions(self) -> Conditions: ...
    @property
    def orders(self) -> Orders: ...
    @property
    def limits(self) -> Limits: ...

    def execute(self) -> list[dict]: ...

