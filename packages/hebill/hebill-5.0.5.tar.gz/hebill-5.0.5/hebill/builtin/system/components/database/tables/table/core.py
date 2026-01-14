from ......functions.decorators import parse_self_x_item_value, \
    parse_self_x_item_value_or_set_by_instance_he_by_module_name
from .....types.he import He


class Table(He):
    def __init__(self, u, name):
        He.__init__(self, u)
        self.__x__['name'] = name
    @property
    def __database__(self): return self.__tables__.__database__
    @property
    def __tables__(self): return self.__u__
    @property
    def __connection__(self): return self.__database__.connection
    @property
    def __configs__(self): return self.__database__.configs
    @property
    @parse_self_x_item_value()
    def name(self): return
    @property
    @parse_self_x_item_value_or_set_by_instance_he_by_module_name()
    def columns(self): return
    @property
    @parse_self_x_item_value_or_set_by_instance_he_by_module_name()
    def data(self): return
    @property
    @parse_self_x_item_value()
    def fullname(self): return f'{self.__configs__['prefix']}{self.name}'

    def exists(self): return self.name in self.__tables__.search_names()
    def create(self): return self.__connection__.create_table(self.fullname)
    def delete(self): return self.__connection__.delete_table(self.fullname)