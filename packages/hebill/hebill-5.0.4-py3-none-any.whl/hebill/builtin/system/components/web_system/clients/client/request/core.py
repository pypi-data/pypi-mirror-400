from .......functions.decorators import parse_self_item_value_or_set_by_instance_he_by_module_name, \
    parse_self_item_value, parse_self_item_value_or_set_by_func
from ......types.hd import Hd


class Request(Hd):
    @property
    def __websystem__(self): return self.__clients__.__websystem__
    @property
    def __clients__(self): return self.__client__.__clients__
    @property
    def __client__(self): return self.__u__
    @property
    def __configs__(self): return self.__websystem__.configs

    @property
    @parse_self_item_value_or_set_by_instance_he_by_module_name()
    def headers(self): return

    @property
    @parse_self_item_value_or_set_by_func()
    def address(self): return self.__client__.address()

    @property
    @parse_self_item_value_or_set_by_instance_he_by_module_name()
    def arguments(self): return

    @property
    @parse_self_item_value_or_set_by_instance_he_by_module_name()
    def form(self): return

    @property
    @parse_self_item_value()
    def method(self): return
    def is_method_post(self): return self.method.upper() == 'POST'
    def is_method_get(self): return self.method.upper() == 'GET'

    @property
    @parse_self_item_value()
    def url(self): return

    @property
    @parse_self_item_value()
    def path(self): return

    @property
    @parse_self_item_value()
    def remote_addr(self): return
