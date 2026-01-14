from ...__data__ import Data


class PaginationSelect(Data):
    @property
    def columns(self): return self.__columns__
    @property
    def conditions(self): return self.__conditions__
    @property
    def orders(self): return self.__orders__

    def execute(self, page_number, items_per_page):
        self.__limits__.set(page_number * (items_per_page - 1), items_per_page)
        return self.__queries__.select_from_table(self.__table__.fullname, self.columns, self.conditions, self.orders, self.__limits__)
