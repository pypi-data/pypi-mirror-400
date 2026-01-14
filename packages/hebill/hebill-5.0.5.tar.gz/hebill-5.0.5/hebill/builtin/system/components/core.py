from types import ModuleType
from .file import File
from ...functions.decorators import instance_he_by_module_name, parse_self_x_item_value_or_set_by_func
from ..types.he import He


class Components(He):
    _a0 = {'arg0':'__s__'}

    @instance_he_by_module_name(**_a0)
    def cls_type(self, pycls: He | type): return
    @instance_he_by_module_name(**_a0)
    def configs(self, data=None, end_class=None, start_class=None, file=None): return
    @instance_he_by_module_name(**_a0)
    def css_maker(self, file: str | File = None): return

    @instance_he_by_module_name(**_a0)
    def database(self, host=None, user=None, password=None, dbname=None, port=None, prefix=None, connection=None, configs:dict=None): return
    @instance_he_by_module_name(**_a0)
    def debugs(self): return

    @instance_he_by_module_name(**_a0)
    def exe_packer(self, u, mainpy:str, website_module:str=None, one_file:bool=False, one_dir:bool=False, show_console:bool=False, pack_overwrite:bool=False): return

    @instance_he_by_module_name(**_a0)
    def file(self, path: str): return
    @instance_he_by_module_name(**_a0)
    def folder(self): return

    @instance_he_by_module_name(**_a0)
    def image(self, source: str): return

    @instance_he_by_module_name(**_a0)
    def htmdoc(self): return

    @instance_he_by_module_name(**_a0)
    def mod_path(self, name: str | ModuleType | type | He): return
    @instance_he_by_module_name(**_a0)
    def mod_type(self, pymod: ModuleType | type | He): return
    @instance_he_by_module_name(**_a0)
    def multilinguals(self, end_pycls=None, start_pycls=None, folder=None, hooked_configs=None, hooked_config_name=None): return

    @instance_he_by_module_name(**_a0)
    def obj_type(self, pyobj: He): return

    @instance_he_by_module_name(**_a0)
    def pip_publisher(self, name: str): return

    @instance_he_by_module_name(**_a0)
    def web_system(self, module: str, host: str = None, port: int = None, db_host: str=None, db_user: str=None, db_password: str=None, db_dbname: str=None, db_port: int=None, db_prefix: str=None, configs:dict=None): return

    @property
    @parse_self_x_item_value_or_set_by_func()
    def image_icon_yangs(self): from .image import IconYangs; return IconYangs(self.__s__)
    @property
    @parse_self_x_item_value_or_set_by_func()
    def image_icon_hebill(self): from .image import IconHebill; return IconHebill(self.__s__)