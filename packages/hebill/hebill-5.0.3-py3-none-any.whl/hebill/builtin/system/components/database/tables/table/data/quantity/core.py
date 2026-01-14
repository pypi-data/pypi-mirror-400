from ...__data__ import Data


class Quantity(Data):
    @property
    def conditions(self): return self.__conditions__
    def execute(self): return self.__queries__.select_count_from_table(self.__table__.fullname, self.conditions)
