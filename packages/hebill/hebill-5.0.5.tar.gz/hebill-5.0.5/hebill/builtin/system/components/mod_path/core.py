from types import ModuleType
from ...types.he import He
from ...types.hs import Hs
from ....functions.builtins import (
    parse_mod_path_by_pycls, parse_mod_path_by_pyobj, import_pymod_by_mod_path, import_pycls_by_mod_path,
    parse_mod_path_by_rel_path
)
from ....functions.decorators import parse_self_x_item_value_or_set_by_func


class ModPath(Hs):
    def __new__(cls, u, name: str | ModuleType | type | He):
        if isinstance(name, He):
            obj = Hs.__new__(cls, u, parse_mod_path_by_pyobj(name))
        elif isinstance(name, type) and issubclass(name, He):
            obj = Hs.__new__(cls, u, parse_mod_path_by_pycls(name))
        elif isinstance(name, ModuleType):
            obj = Hs.__new__(cls, u, name.__name__)
        elif isinstance(name, str):
            obj = Hs.__new__(cls, u, name)
        else:
            raise ValueError(f'ModName 的参数 name 只允许： He | types.ModuleType | type(He) | str')
        return obj

    def __init__(self, u, name: str | ModuleType | type | He):
        if isinstance(name, He):
            Hs.__init__(self, u, parse_mod_path_by_pyobj(name))
            self.__x__['pycls'] = name.__class__
            self.__x__['pymod'] = name.__module__
        elif isinstance(name, type) and issubclass(name, He):
            Hs.__init__(self, u, parse_mod_path_by_pycls(name))
            self.__x__['pycls'] = name
            self.__x__['pymod'] = name.__module__
        elif isinstance(name, ModuleType):
            Hs.__init__(self, u, name.__name__)
            self.__x__['pymod'] = name
        elif isinstance(name, str):
            Hs.__init__(self, u, name)

    @property
    @parse_self_x_item_value_or_set_by_func()
    def pymod(self):
        try: return import_pymod_by_mod_path(self)
        except: return None
    @property
    @parse_self_x_item_value_or_set_by_func()
    def pycls(self):
        try: return import_pycls_by_mod_path(self)
        except: return None

    @property
    @parse_self_x_item_value_or_set_by_func()
    def mod_type(self):
        if self.pycls: return self.__sm__.mod_type(self.pycls)
        if self.pymod: return self.__sm__.mod_type(self.pymod)
        return None

    @property
    @parse_self_x_item_value_or_set_by_func()
    def cls_type(self):
        if self.pycls: return self.__sm__.cls_type(self.pycls)
        return None

    def rel_mod_path(self, rel_path=None):
        return ModPath(self.__s__, parse_mod_path_by_rel_path(self, rel_path))
