from ....functions.builtins import parse_mod_path_by_pyobj, parse_mod_path_by_pycls
from ....functions.decorators import parse_self_x_item_value, parse_self_x_item_value_or_set_by_func
from ...types.he import He
from ...types.hs import Hs


class ClsType(Hs):
    def __new__(cls, u, pycls: He | type):
        if isinstance(pycls, He):
            obj = Hs.__new__(cls, u, parse_mod_path_by_pyobj(pycls))
        elif issubclass(pycls, He):
            obj = Hs.__new__(cls, u, parse_mod_path_by_pycls(pycls))
        else:
            raise ValueError(f'ClsType 的参数 pycls 只允许： He | type(He)')
        return obj

    def __init__(self, u, pycls: He | type):
        if isinstance(pycls, He):
            Hs.__init__(self, u, parse_mod_path_by_pyobj(pycls))
            self.__x__['pycls'] = pycls.__class__
            self.__x__['pymod'] = pycls.__module__
        elif issubclass(pycls, He):
            Hs.__init__(self, u, parse_mod_path_by_pycls(pycls))
            self.__x__['pycls'] = pycls
            self.__x__['pymod'] = pycls.__module__
        else:
            raise ValueError(f'ClsType 的参数 pycls 只允许： He | type(He)')

    @property
    @parse_self_x_item_value()
    def pymod(self): return
    @property
    @parse_self_x_item_value()
    def pycls(self): return
    @property
    def mod_path(self): return self.mod_type.mod_path
    @property
    @parse_self_x_item_value_or_set_by_func()
    def mod_type(self): return self.__sm__.mod_type(self.pycls)

    @property
    @parse_self_x_item_value_or_set_by_func()
    def tree_pyclses(self): return [i for i in self.pycls.mro() if issubclass(i, He)]
    @property
    @parse_self_x_item_value_or_set_by_func()
    def tree_cls_types(self): return [self.__sm__.cls_type(i) for i in self.tree_pyclses]

    def has_function(self, name): return callable(self.pycls.__dict__.get(name))
    def has_local_function(self, name): return callable(getattr(self.pycls, name, None))

    @property
    def folder(self): return self.mod_type.folder
    @property
    def data_folder(self): return self.mod_type.data_folder
    @property
    def data_configs_folder(self): return self.mod_type.data_configs_folder
    @property
    def data_configs_file(self): return self.mod_type.data_configs_file
    @property
    def logs_folder(self): return self.mod_type.logs_folder
    @property
    def data_multilinguals_folder(self): return self.mod_type.data_multilinguals_folder
    def data_multilinguals_file(self, language: str): return self.mod_type.data_multilinguals_file(language)
    @property
    def data_database_tables_folder(self): return self.mod_type.data_database_tables_folder
    @property
    def data_database_data_folder(self): return self.mod_type.data_database_data_folder

    @property
    @parse_self_x_item_value_or_set_by_func()
    def multilinguals(self): return self.__sm__.multilinguals(self.pycls, He, hooked_configs=self.__sc__)
    def ml(self, code, language=None, replace=None, return_code=None): return self.multilinguals.ml(code, language, replace, return_code)
    def ml_name(self, language=None, replace=None, return_code=None): return self.multilinguals.ml_name(language, replace, return_code)
    def ml_abbreviation(self, language=None, replace=None, return_code=None): return self.multilinguals.ml_abbreviation(language, replace, return_code)
    def ml_title(self, language=None, replace=None, return_code=None): return self.multilinguals.ml_title(language, replace, return_code)
    def ml_description(self, language=None, replace=None, return_code=None): return self.multilinguals.ml_description(language, replace, return_code)
    def ml_link_title(self, language=None, replace=None, return_code=None): return self.multilinguals.ml_link_title(language, replace, return_code)
    def ml_page_title(self, language=None, replace=None, return_code=None): return self.multilinguals.ml_page_title(language, replace, return_code)
    def ml_breadcrumb_title(self, language=None, replace=None, return_code=None): return self.multilinguals.ml_breadcrumb_title(language, replace, return_code)
