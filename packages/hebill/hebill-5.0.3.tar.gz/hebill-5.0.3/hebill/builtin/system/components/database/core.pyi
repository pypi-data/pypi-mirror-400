from ...types.he import He
from .configs import Configs
from .connection import Connection
from .tables import Tables

class Database(He):

    def __init__(self, u, host: str = None, user: str = None, password: str = None, dbname: str = None, port: int = None, prefix: str = None, connection: str = None, configs:dict=None): ...

    @property
    def configs(self)-> Configs: ...
    @property
    def tables(self)-> Tables: ...
    @property
    def connection(self)-> Connection: ...
