from ......types.he import He
from .column import Column


class Columns(He):
    @property
    def __database__(self): return self.__table__.__database__
    @property
    def __tables__(self): return self.__table__.__tables__
    @property
    def __table__(self): return self.__u__
    @property
    def __connection__(self): return self.__database__.connection
    @property
    def __configs__(self): return self.__database__.configs

    def column(self, name): return Column(self, name)

    def search_names(self, keyword=None, startwith=None, endwith=None): return self.__connection__.search_table_columns(self.__table__.fullname, keyword, startwith, endwith)
