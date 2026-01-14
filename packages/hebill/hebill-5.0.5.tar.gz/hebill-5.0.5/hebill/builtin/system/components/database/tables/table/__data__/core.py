from .......functions.decorators import parse_self_x_item_value
from ....connections.mysql.plugins.columns import Columns
from ....connections.mysql.plugins.conditions import Conditions
from ....connections.mysql.plugins.limits import Limits
from ....connections.mysql.plugins.orders import Orders
from ......types.he import He


class Data(He):
    def __init__(self, table, columns=None, conditions=None, orders=None, limits=None):
        He.__init__(self, table)
        if columns: self.__x__['__columns__'] = columns
        if conditions: self.__x__['__conditions__'] = conditions
        if orders: self.__x__['__orders__'] = orders
        if limits: self.__x__['__limits__'] = limits

    @property
    def __database__(self): return self.__table__.__database__
    @property
    def __tables__(self): return self.__table__.__tables__
    @property
    def __table__(self): return self.__s__
    @property
    def __configs__(self): return self.__database__.configs

    @property
    @parse_self_x_item_value()
    def __columns__(self): return Columns()
    @property
    @parse_self_x_item_value()
    def __conditions__(self): return Conditions()
    @property
    @parse_self_x_item_value()
    def __limits__(self): return Limits()
    @property
    @parse_self_x_item_value()
    def __orders__(self): return Orders()
