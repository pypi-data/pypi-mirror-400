from ........functions.decorators import parse_self_x_item_value
from .......types.he import He


class Column(He):
    def __init__(self, u, name):
        He.__init__(self, u)
        self.__x__['name'] = name
    @property
    def __database__(self): return self.__columns__.__database__
    @property
    def __tables__(self): return self.__columns__.__tables__
    @property
    def __table__(self): return self.__columns__.__table__
    @property
    def __columns__(self): return self.__u__
    @property
    def __connection__(self): return self.__database__.connection
    @property
    def __configs__(self): return self.__database__.configs

    @property
    @parse_self_x_item_value()
    def name(self): return

    def exists(self): return self.name in self.__columns__.search_names()
    def create(self, datatype=None, length=0, unique=False, nullable=False): return self.__connection__.create_table_column(self.__table__.fullname, self.name, datatype, length, unique, nullable)
    def delete(self): return

    def set_unique(self): return self.__connection__.set_table_column_quniue(self.__table__.fullname, self.name)
