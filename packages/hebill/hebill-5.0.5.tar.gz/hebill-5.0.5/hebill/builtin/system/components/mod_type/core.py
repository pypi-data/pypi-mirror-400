from types import ModuleType

from ....functions.builtins import parse_mod_path_by_pyobj, parse_mod_path_by_pycls, import_pycls_by_mod_path, parse_dirpath_by_pymod
from ....functions.decorators import parse_self_x_item_value_or_set_by_func, parse_self_x_item_value
from ...types.he import He
from ...types.hs import Hs



class ModType(Hs):
    def __new__(cls, u, pymod: ModuleType | type | He):
        if isinstance(pymod, He):
            obj = Hs.__new__(cls, u, parse_mod_path_by_pyobj(pymod))
        elif isinstance(pymod, type) and issubclass(pymod, He):
            obj = Hs.__new__(cls, u, parse_mod_path_by_pycls(pymod))
        elif isinstance(pymod, ModuleType):
            obj = Hs.__new__(cls, u, pymod.__name__)
        else:
            raise ValueError(f'ModType 的参数 pymod 只允许： He | types.ModuleType | type(He)')
        return obj

    def __init__(self, u: He, pymod: ModuleType | type | He):
        if isinstance(pymod, He):
            Hs.__init__(self, u, parse_mod_path_by_pyobj(pymod))
            self.__x__['pycls'] = pymod.__class__
            self.__x__['pymod'] = __import__(pymod.__module__, fromlist=[''])
        elif isinstance(pymod, type) and issubclass(pymod, He):
            Hs.__init__(self, u, parse_mod_path_by_pycls(pymod))
            self.__x__['pycls'] = pymod
            self.__x__['pymod'] = __import__(pymod.__module__, fromlist=[''])
        elif isinstance(pymod, ModuleType):
            Hs.__init__(self, u, pymod.__name__)
            self.__x__['pymod'] = pymod

    @property
    @parse_self_x_item_value()
    def pymod(self): return
    @property
    @parse_self_x_item_value_or_set_by_func()
    def pycls(self):
        try: return import_pycls_by_mod_path(self)
        except: return None

    @property
    @parse_self_x_item_value_or_set_by_func()
    def mod_path(self): return self.__sm__.mod_path(self)

    @property
    @parse_self_x_item_value_or_set_by_func()
    def cls_type(self):
        if self.pycls: return self.__sm__.cls_type(self.pycls)
        return None

    def rel_mod_path(self, rel_path=None): return self.mod_path.rel_mod_path(rel_path)
    def rel_mod_type(self, rel_path=None): return self.rel_mod_path(rel_path).mod_type

    @property
    @parse_self_x_item_value_or_set_by_func()
    def folder(self): return self.__sm__.folder(parse_dirpath_by_pymod(self.pymod))

    @property
    @parse_self_x_item_value_or_set_by_func()
    def data_folder(self): return self.folder.child_folder(self.__si__.DIRNAM_DATA)
    @property
    @parse_self_x_item_value_or_set_by_func()
    def data_configs_folder(self): return self.data_folder.child_folder(self.__si__.DIRNAM_DATA_CONFIGS)
    @property
    @parse_self_x_item_value_or_set_by_func()
    def data_configs_file(self): return self.data_configs_folder.child_file(self.__si__.FILNAM_CONFIGS)
    @property
    @parse_self_x_item_value_or_set_by_func()
    def data_database_tables_folder(self): return self.data_folder.child_folder(self.__si__.DIRNAM_DATA_DATABASE_TABLES)
    def data_database_table_file(self, name): return self.data_database_tables_folder.child_file(f'{name}.json')
    @property
    @parse_self_x_item_value_or_set_by_func()
    def data_database_data_folder(self): return self.data_folder.child_folder(self.__si__.DIRNAM_DATA_DATABASE_DATA)
    def data_database_data_file(self, name): return self.data_database_data_folder.child_file(f'{name}.json')
    @property
    @parse_self_x_item_value_or_set_by_func()
    def data_multilinguals_folder(self): return self.data_folder.child_folder(self.__si__.DIRNAM_DATA_MULTILINGALS)
    def data_multilinguals_file(self, language): return self.data_multilinguals_folder.child_file(f'{language}.json')

    @property
    @parse_self_x_item_value_or_set_by_func()
    def logs_folder(self): return self.folder.child_folder(self.__si__.DIRNAM_LOGS)

    @property
    @parse_self_x_item_value_or_set_by_func()
    def public_folder(self): return self.folder.child_folder(self.__si__.DIRNAM_PUBLIC)

    @property
    @parse_self_x_item_value_or_set_by_func()
    def multilinguals(self): return self.__sm__.multilinguals(folder=self.data_multilinguals_folder, hooked_configs=self.__sc__)
    def ml(self, code, language=None, replace=None, return_code=None): return self.multilinguals.ml(code, language, replace, return_code)
    def ml_name(self, language=None, replace=None, return_code=None): return self.multilinguals.ml_name(language, replace, return_code)
    def ml_abbreviation(self, language=None, replace=None, return_code=None): return self.multilinguals.ml_abbreviation(language, replace, return_code)
    def ml_title(self, language=None, replace=None, return_code=None): return self.multilinguals.ml_title(language, replace, return_code)
    def ml_description(self, language=None, replace=None, return_code=None): return self.multilinguals.ml_description(language, replace, return_code)
    def ml_link_title(self, language=None, replace=None, return_code=None): return self.multilinguals.ml_link_title(language, replace, return_code)
    def ml_page_title(self, language=None, replace=None, return_code=None): return self.multilinguals.ml_page_title(language, replace, return_code)
    def ml_breadcrumb_title(self, language=None, replace=None, return_code=None): return self.multilinguals.ml_breadcrumb_title(language, replace, return_code)
