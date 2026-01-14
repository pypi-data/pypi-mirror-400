from ....functions.builtins import parse_mod_path_by_pyobj
from ....functions.decorators import parse_self_x_item_value, parse_self_x_item_value_or_set_by_func
from ...types.he import He
from ...types.hs import Hs


class ObjType(Hs):
    def __init__(self, u, pyobj: He):
        if isinstance(pyobj, He):
            Hs.__init__(self, u, parse_mod_path_by_pyobj(pyobj))
            self.__x__['pyobj'] = pyobj
            self.__x__['pycls'] = pyobj.__class__
            self.__x__['pymod'] = pyobj.__module__
        else:
            raise ValueError(f'ObjType 的参数 pyobj 只允许： He')

    @property
    @parse_self_x_item_value()
    def pymod(self): return self.mod_type.pymod
    @property
    @parse_self_x_item_value()
    def pycls(self): return self.cls_type.pycls
    @property
    @parse_self_x_item_value()
    def pyobj(self): return

    @property
    def mod_path(self): return self.mod_type.mod_path
    @property
    def mod_type(self): return self.cls_type.mod_type
    @property
    @parse_self_x_item_value_or_set_by_func()
    def cls_type(self): return self.__sm__.cls_type(self.pyobj)

    @property
    @parse_self_x_item_value_or_set_by_func()
    def tree_pyclses(self): return self.cls_type.tree_pyclses
    @property
    def tree_cls_types(self): return self.cls_type.tree_cls_types

    def has_function(self, name): return callable(self.pycls.__dict__.get(name))
    def has_local_function(self, name): return callable(getattr(self.pycls, name, None))

    @property
    def folder(self): return self.cls_type.folder
    @property
    def data_folder(self): return self.cls_type.data_folder
    @property
    def data_configs_folder(self): return self.cls_type.data_configs_folder
    @property
    def data_configs_file(self): return self.cls_type.data_configs_file
    @property
    def logs_folder(self): return self.cls_type.logs_folder
    @property
    def data_multilinguals_folder(self): return self.cls_type.data_multilinguals_folder
    def data_multilinguals_file(self, language: str): return self.cls_type.data_multilinguals_file(language)
    @property
    def data_database_tables_folder(self): return self.cls_type.data_database_tables_folder
    @property
    def data_database_data_folder(self): return self.cls_type.data_database_data_folder

    @property
    def multilinguals(self): return self.cls_type.multilinguals
    def ml(self, code, language=None, replace=None, return_code=None): return self.multilinguals.ml(code, language, replace, return_code)
    def ml_name(self, language=None, replace=None, return_code=None): return self.multilinguals.ml_name(language, replace, return_code)
    def ml_abbreviation(self, language=None, replace=None, return_code=None): return self.multilinguals.ml_abbreviation(language, replace, return_code)
    def ml_title(self, language=None, replace=None, return_code=None): return self.multilinguals.ml_title(language, replace, return_code)
    def ml_description(self, language=None, replace=None, return_code=None): return self.multilinguals.ml_description(language, replace, return_code)
    def ml_link_title(self, language=None, replace=None, return_code=None): return self.multilinguals.ml_link_title(language, replace, return_code)
    def ml_page_title(self, language=None, replace=None, return_code=None): return self.multilinguals.ml_page_title(language, replace, return_code)
    def ml_breadcrumb_title(self, language=None, replace=None, return_code=None): return self.multilinguals.ml_breadcrumb_title(language, replace, return_code)