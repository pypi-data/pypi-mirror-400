from .....functions.builtins import parse_mod_path_by_pyobj
from .....functions.decorators import parse_self_x_item_value_or_set_by_func, parse_self_x_item_value


class I:
    def __init__(self, he):
        self.__x = {}
        self.__x__['__he__'] = he
    @property
    def __x__(self): return self.__x
    @property
    @parse_self_x_item_value()
    def __he__(self): return

    @property
    def id(self): return self.__he__.__id__
    @property
    @parse_self_x_item_value_or_set_by_func()
    def mod_path(self): return self.__he__.__s__.components.mod_path(parse_mod_path_by_pyobj(self.__he__))
    @property
    def mod_type(self): return self.mod_path.mod_type
    @property
    def cls_type(self): return self.mod_path.cls_type
    @property
    @parse_self_x_item_value_or_set_by_func()
    def obj_type(self): return self.__he__.__s__.components.obj_type(self.__he__)

    @property
    def folder(self): return self.cls_type.folder
