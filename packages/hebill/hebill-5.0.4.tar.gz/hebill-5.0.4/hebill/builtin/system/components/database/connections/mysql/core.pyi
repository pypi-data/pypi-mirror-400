from dbutils.pooled_db import PooledDB
from pymysql.cursors import DictCursor

from ....database import Database
from ....database.connection import Connection


class Mysql(Connection):
    @property
    def __u__(self)-> Database: ...
    @property
    def __pool__(self)-> PooledDB: ...
    @property
    def __is_connected__(self)-> bool: ...

    def query(self, sql: str)-> DictCursor | None: ...