from ...__data__ import Data
from .....queries.plugins.columns import Columns
from .....queries.plugins.conditions import Conditions
from .....queries.plugins.orders import Orders


class PaginationSelect(Data):
    @property
    def columns(self) -> Columns: ...
    @property
    def conditions(self) -> Conditions: ...
    @property
    def orders(self) -> Orders: ...

    def execute(self, page_number: int, items_per_page: int) -> list[dict]: ...

