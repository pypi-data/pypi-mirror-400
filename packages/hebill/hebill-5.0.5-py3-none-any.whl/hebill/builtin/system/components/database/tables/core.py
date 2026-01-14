from ....types.he import He
from .table import Table


class Tables(He):
    @property
    def __database__(self): return self.__u__
    @property
    def __connection__(self): return self.__database__.connection
    @property
    def __configs__(self): return self.__database__.configs

    def table(self, name): return Table(self, name)

    def search_names(self, keyword=None, startwith=None, endwith=None):
        if keyword and startwith: keyword = self.__configs__['prefix'] + keyword
        return self.__connection__.search_tables(keyword, startwith, endwith)
