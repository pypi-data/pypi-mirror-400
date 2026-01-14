from ...__data__ import Data


class Select(Data):
    @property
    def columns(self): return self.__columns__
    @property
    def conditions(self): return self.__conditions__
    @property
    def orders(self): return self.__orders__
    @property
    def limits(self): return self.__limits__

    def execute(self): return self.__queries__.select_from_table(self.__table__.fullname, self.columns, self.conditions, self.orders, self.limits)
