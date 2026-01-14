from ......types.he import He
from .quantity import Quantity
from .drop import Drop
from .update import Update
from .select import Select
from .pagination_select import PaginationSelect


class Data(He):
    def __init__(self, u):
        He.__init__(self, u)
    @property
    def __database__(self): return self.__tables__.__database__
    @property
    def __tables__(self): return self.__table__.__tables__
    @property
    def __table__(self): return self.__u__
    @property
    def __configs__(self): return self.__database__.configs
    @property
    def __queries__(self): return self.__database__.queries

    def quantity_obj(self, conditions=None): return Quantity(self.__table__, conditions=conditions)
    def quantity(self, conditions=None): return self.quantity_obj(conditions).execute()
    def drop_obj(self, conditions=None): return Drop(self.__table__, conditions=conditions)
    def drop(self, conditions=None): return self.drop_obj(conditions).execute()
    def insert(self, data, user=None, keywords=None): return self.__queries__.insert_into_table(self.__table__.fullname, data, user, keywords)
    def update_obj(self, conditions=None): return Update(self.__table__, conditions=conditions)
    def update(self, data, conditions=None): return self.update_obj(conditions).execute(data)
    def select_obj(self, columns=None, conditions=None, orders=None, limits=None): return Select(self.__table__, columns, conditions, orders, limits)
    def select(self, columns=None, conditions=None, orders=None, limits=None): return self.select_obj(columns, conditions, orders, limits).execute()
    def pagination_select_obj(self, columns=None, conditions=None, orders=None): return PaginationSelect(self.__table__, columns, conditions, orders)
    def pagination_select(self, page_number, items_per_page, columns=None, conditions=None, orders=None): return self.pagination_select_obj(columns, conditions, orders).execute(page_number, items_per_page)
