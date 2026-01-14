from ...types.he import He
from ....functions.builtins import HeEro
from ....functions.decorators import parse_self_x_item_value_or_set_by_func, \
    parse_self_x_item_value_or_set_by_instance_he_by_module_name


class WebSystem(He):
    def __init__(self, u, module: str, host: str=None, port: int=None, db_host: str=None, db_user: str=None, db_password: str=None, db_dbname: str=None, db_port: int=None, db_prefix: str=None, configs:dict=None):
        ero = HeEro(WebSystem, '__init__', '网站系统实例化')
        super().__init__(u)
        self.configs.update(configs)
        """设置参数"""
        self.configs.module = module
        self.configs.host = host
        self.configs.port = port
        self.configs.mysql_host = db_host
        self.configs.mysql_user = db_user
        self.configs.mysql_password = db_password
        self.configs.mysql_dbname = db_dbname
        self.configs.mysql_port = db_port
        self.configs.mysql_prefix = db_prefix
        # 由于在 Config.__init__ 调用时候 'module', 'host', 'port' 还未设置，会造成死循环，所以在这里更新网站系统设置
        if not self.is_website_exists():
            raise ero.add(f'网站系统设置的网站根模块 {self.configs.module} 不存在')
        if self.website_mod_type.data_configs_file.is_exists():
            if isinstance(data:=self.website_mod_type.data_configs_file.parse_json(), dict):
                for k, v in data.items():
                    if k not in ['module', 'host', 'port']:
                        self.configs.set(k, v)

    @property
    @parse_self_x_item_value_or_set_by_func()
    def __debugs_prefix__(self): return [self.configs.module]

    @property
    @parse_self_x_item_value_or_set_by_instance_he_by_module_name()
    def configs(self): return

    @property
    @parse_self_x_item_value_or_set_by_instance_he_by_module_name()
    def database(self): return

    @property
    @parse_self_x_item_value_or_set_by_func()
    def server(self): from .servers.flask_server import FlaskServer; return FlaskServer(self)

    @property
    @parse_self_x_item_value_or_set_by_instance_he_by_module_name()
    def clients(self): return

    @property
    @parse_self_x_item_value_or_set_by_func()
    def website_mod_path(self): return self.__sm__.mod_path(self.configs.module)
    @property
    def website_mod_type(self): return self.website_mod_path.mod_type
    def is_website_exists(self): return self.website_mod_type is not None
    @property
    def website_folder(self): return self.website_mod_type.folder if self.is_website_exists() else None
