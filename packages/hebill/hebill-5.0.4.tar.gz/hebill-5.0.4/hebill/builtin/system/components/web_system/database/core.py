from ...database import Database as PluginDatabase


class Database(PluginDatabase):
    def __init__(self, system):
        super().__init__(system)
        self.configs.hook('mysql_host', system.configs, 'host')
        self.configs.hook('mysql_user', system.configs, 'user')
        self.configs.hook('mysql_password', system.configs, 'password')
        self.configs.hook('mysql_dbname', system.configs, 'dbname')
        self.configs.hook('mysql_port', system.configs, 'port')
        self.configs.hook('mysql_prefix', system.configs, 'prefi')
