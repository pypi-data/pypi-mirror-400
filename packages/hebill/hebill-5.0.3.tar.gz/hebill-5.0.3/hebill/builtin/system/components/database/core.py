from ....functions.decorators import parse_self_x_item_value_or_set_by_func, \
    parse_self_x_item_value_or_set_by_instance_he_by_module_name
from ...types.he import He


class Database(He):
    def __init__(self, u, host=None, user=None, password=None, dbname=None, port=None, prefix=None, connection=None, configs:dict=None):
        He.__init__(self, u)
        self.configs.update(configs)
        self.configs['host'] = host
        self.configs['user'] = user
        self.configs['password'] = password
        self.configs['dbname'] = dbname
        self.configs['port'] = port or 3306
        self.configs['prefix'] = prefix or ''
        self.configs['connection'] = connection or 'mysql'

    @property
    @parse_self_x_item_value_or_set_by_instance_he_by_module_name()
    def configs(self): return

    @property
    @parse_self_x_item_value_or_set_by_instance_he_by_module_name()
    def tables(self): return

    @property
    @parse_self_x_item_value_or_set_by_func()
    def connection(self):
        if self.configs['connection'] == 'mysql':
            from .connections.mysql import Mysql
            return Mysql(self)
        return None
