from ......types.he import He
from .... import Database
from ... import Tables
from ...table import Table
from ....configs import Configs
from ....connections.mysql.plugins.columns import Columns
from ....connections.mysql.plugins.conditions import Conditions
from ....connections.mysql.plugins.limits import Limits
from ....connections.mysql.plugins.orders import Orders


class Data(He):
    def __init__(self, table: Table, columns: Columns=None, conditions: Conditions=None, orders: Orders=None, limits: Limits=None):
        ...
    @property
    def __database__(self) -> Database: ...
    @property
    def __tables__(self) -> Tables: ...
    @property
    def __table__(self) -> Table: ...
    @property
    def __configs__(self)-> Configs: ...

    @property
    def __columns__(self) -> Columns: ...
    @property
    def __conditions__(self) -> Conditions: ...
    @property
    def __limits__(self) -> Limits: ...
    @property
    def __orders__(self) -> Orders: ...
