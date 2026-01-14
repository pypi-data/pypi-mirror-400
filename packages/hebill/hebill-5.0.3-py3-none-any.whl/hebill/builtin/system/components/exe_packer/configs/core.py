from .....functions.decorators import parse_self_item_value, set_self_item_value_by_setter_with_agr
from ...configs import Configs as PluCfg


class Configs(PluCfg):
    @property
    @parse_self_item_value()
    def website_module(self): return
    @website_module.setter
    @set_self_item_value_by_setter_with_agr(value_type='strue')
    def website_module(self, value): pass

    @property
    @parse_self_item_value()
    def mainpy(self): return
    @mainpy.setter
    @set_self_item_value_by_setter_with_agr(value_type='strue')
    def mainpy(self, value): pass

    @property
    @parse_self_item_value()
    def exe_name(self): return
    @exe_name.setter
    @set_self_item_value_by_setter_with_agr(value_type='strue')
    def exe_name(self, value): pass

    @property
    @parse_self_item_value()
    def show_console(self): return
    @show_console.setter
    @set_self_item_value_by_setter_with_agr(value_type='bol')
    def show_console(self, value): pass

    @property
    @parse_self_item_value()
    def one_file(self): return
    @one_file.setter
    @set_self_item_value_by_setter_with_agr(value_type='bol')
    def one_file(self, value): pass

    @property
    @parse_self_item_value()
    def one_dir(self): return
    @one_dir.setter
    @set_self_item_value_by_setter_with_agr(value_type='bol')
    def one_dir(self, value): pass

    @property
    @parse_self_item_value()
    def pack_overwrite(self): return
    @pack_overwrite.setter
    @set_self_item_value_by_setter_with_agr(value_type='bol')
    def pack_overwrite(self, value): pass

    @property
    @parse_self_item_value()
    def root_folders(self): return
    @root_folders.setter
    @set_self_item_value_by_setter_with_agr(value_type='lst')
    def root_folders(self, value): pass

    @property
    @parse_self_item_value()
    def root_modules(self): return
    @root_modules.setter
    @set_self_item_value_by_setter_with_agr(value_type='lst')
    def root_modules(self, value): pass

    @property
    @parse_self_item_value()
    def dist_path(self): return
    @dist_path.setter
    @set_self_item_value_by_setter_with_agr()
    def dist_path(self, value): pass

    @property
    @parse_self_item_value()
    def build_path(self): return
    @build_path.setter
    @set_self_item_value_by_setter_with_agr()
    def build_path(self, value): pass

    @property
    @parse_self_item_value()
    def spec_path(self): return
    @spec_path.setter
    @set_self_item_value_by_setter_with_agr()
    def spec_path(self, value): pass

    @property
    @parse_self_item_value()
    def comd_path(self): return
    @comd_path.setter
    @set_self_item_value_by_setter_with_agr()
    def comd_path(self, value): pass

    @property
    @parse_self_item_value()
    def icon_file(self): return
    @icon_file.setter
    @set_self_item_value_by_setter_with_agr()
    def icon_file(self, value): pass

    @property
    @parse_self_item_value()
    def version_file(self): return
    @version_file.setter
    @set_self_item_value_by_setter_with_agr()
    def version_file(self, value): pass
