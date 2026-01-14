from ...__data__ import Data


class Update(Data):
    @property
    def conditions(self): return self.__conditions__
    def execute(self, data): return self.__queries__.update_table(self.__table__.fullname, data, self.conditions)
