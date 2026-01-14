from ..folder import Folder
from ....functions.decorators import parse_self_x_item_value, parse_self_x_item_value_or_set_by_func, \
    parse_self_item_value_or_set_by_instance_he_by_module_name
from ...types.he import He
from ...types.hd import Hd


class Multilinguals(Hd):
    def __init__(self, u, end_pycls=None, start_pycls=None, folder=None, hooked_configs=None, hooked_config_name=None):
        super().__init__(u)
        if folder:
            if isinstance(folder, Folder): self.__x__['folder'] = folder
            else:  self.__x__['folder'] = self.__sm__.folder(folder)
        elif end_pycls:
            start_pycls = start_pycls if start_pycls else He
            if not issubclass(end_pycls, He): raise RuntimeError('senior_class 必须是继承自 Heobj 的类或者实例')
            if not issubclass(end_pycls, start_pycls): raise RuntimeError('end_pycls 必须是继承自 start_pycls 的类或者实例')
            for cls in end_pycls.mro():
                if issubclass(cls, start_pycls):
                    self.___tree_cls_types___.append(self.__sm__.cls_type(cls))
        if hooked_configs: self.__x__['hooked_configs'] = hooked_configs
        if hooked_config_name: self.__x__['hooked_config_name'] = hooked_config_name

    @property
    @parse_self_x_item_value_or_set_by_func()
    def ___tree_cls_types___(self): return []
    @property
    @parse_self_x_item_value()
    def ___hooked_configs___(self): return
    @property
    @parse_self_x_item_value()
    def ___hooked_config_name___(self): return

    @property
    @parse_self_x_item_value_or_set_by_func()
    def folder(self): return self.___tree_cls_types___[0].data_multilinguals_folder

    @parse_self_item_value_or_set_by_instance_he_by_module_name(dict_item_key_by_arg=0)
    def package(self, language): return

    @property
    def default(self):
        if self.___hooked_configs___ is not None:
            if (l:=self.___hooked_configs___.___defaults___.get(self.___hooked_config_name___)) is not None:
                return self.package(l)
            return self.runtime
        return self.package(self.__sc__.language)

    @property
    def runtime(self):
        if self.___hooked_configs___ is not None:
            if (l:=self.___hooked_configs___.get(self.___hooked_config_name___)) is not None:
                return self.package(l)
        return self.package(self.__sc__.language)

    def ml(self, code, language=None, replace=None, return_code=None):
        if language and code in self.package(language): return self.package(language).ml(code, replace, return_code)
        if code in self.runtime: return self.runtime.ml(code, replace, return_code)
        if code in self.default: return self.default.ml(code, replace, return_code)
        return replace or code if return_code or return_code is None else None

    def ml_name(self, language=None, replace=None, return_code=None): return self.ml(self.__s__.__si__.MLKEY_NAME, language, replace, return_code)
    def ml_abbreviation(self, language=None, replace=None, return_code=None): return self.ml(self.__si__.MLKEY_ABBR, language, replace, return_code)
    def ml_title(self, language=None, replace=None, return_code=None): return self.ml(self.__si__.MLKEY_TITLE, language, replace, return_code)
    def ml_description(self, language=None, replace=None, return_code=None): return self.ml(self.__si__.MLKEY_DESC, language, replace, return_code)
    def ml_link_title(self, language=None, replace=None, return_code=None): return self.ml(self.__si__.MLKEY_LINK_TITLE, language, replace, return_code)
    def ml_page_title(self, language=None, replace=None, return_code=None): return self.ml(self.__si__.MLKEY_PAGE_TITLE, language, replace, return_code)
    def ml_breadcrumb_title(self, language=None, replace=None, return_code=None): return self.ml(self.__si__.MLKEY_BDCD_TITLE, language, replace, return_code)
