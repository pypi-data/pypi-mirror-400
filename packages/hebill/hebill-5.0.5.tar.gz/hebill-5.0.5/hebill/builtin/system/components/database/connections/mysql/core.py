from ......functions.decorators import parse_self_x_item_value_or_set_by_func, parse_self_x_item_value
from ...connection import Connection
import pymysql
import pymysql.cursors
from dbutils.pooled_db import PooledDB


class Mysql(Connection):
    ########## 使用连接池 ##########
    @property
    @parse_self_x_item_value_or_set_by_func()
    def __pool__(self):
        return PooledDB(
            creator=pymysql,
            maxconnections=self.__u__.configs['max_connections'],
            host=self.__u__.configs['host'],
            user=self.__u__.configs['user'],
            password=self.__u__.configs['password'],
            port=self.__u__.configs['port'],
            database=self.__u__.configs['dbname'],
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
            connect_timeout=self.__u__.configs['connect_timeout']
        )
    @property
    @parse_self_x_item_value()
    def __is_connected__(self): return

    # 平台函数
    def is_connected(self, recheck=False) :
        if not (self.__u__.configs['host'] and self.__u__.configs['port'] and self.__u__.configs['user'] and self.__u__.configs['password'] and self.__u__.configs['dbname']):
            self.__x__['__is_connected__'] = False
        elif recheck or self.__is_connected__ is None:
            try:
                conn = self.__pool__.connection()
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    cursor.fetchone()
                conn.close()
                self.__x__['__is_connected__'] = True
            except Exception:
                self.__x__['__is_connected__'] = False
        return self.__is_connected__

    def query(self, sql):
        self.queried_sqls.append(sql)
        info = f'数据库[{self.__u__.configs['host']}:{self.__u__.configs['port']}/{self.__u__.configs['dbname']}]查询'
        if self.is_connected():
            with self.__pool__.connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(sql)
                    connection.commit()
                    connection.close()
                    self.__s__.debugs.output.success(f'{info}成功：{sql}')
                    return cursor
            """try:
                with self.__pool__.connection() as connection:
                    with connection.cursor() as cursor:
                        cursor.execute(sql)
                        connection.commit()
                        connection.close()
                        self.__s__.debugs.output.success(f'{info}成功：{sql}')
                        return cursor
            except Exception:
                return None"""
        return None

    def search_tables(self, keyword=None, startwith=None, endwith=None):
        sql =  f'SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = "{self.__u__.configs['dbname']}"'
        if keyword: sql += f' AND TABLE_NAME LIKE "{'' if startwith else '%'}{keyword}{'' if endwith else '%'}";'
        response = self.query(sql)
        result = []
        if response is not None:
            for row in response:
                result.append(row['TABLE_NAME'])
        return result

    def create_table(self, table):
        return self.query((
            f'CREATE TABLE IF NOT EXISTS `{table}` ('
            f'`{self.__u__.configs['column_key_sn']}` bigint NOT NULL AUTO_INCREMENT, '
            f'`{self.__u__.configs['column_key_id']}` varchar(64) UNIQUE NOT NULL, '
            f'`{self.__u__.configs['column_key_az']}` bigint NULL, '
            f'`{self.__u__.configs['column_key_kw']}` text NULL, '
            f'`{self.__u__.configs['column_key_ur']}` varchar(64) NOT NULL, '
            f'`{self.__u__.configs['column_key_dc']}` bigint NOT NULL, '
            f'`{self.__u__.configs['column_key_du']}` bigint NOT NULL, '
            f'PRIMARY KEY (`{self.__u__.configs['column_key_sn']}`)) ENGINE=InnoDB DEFAULT CHARACTER SET=utf8 COLLATE=utf8_unicode_ci'
            )) is not None

    def delete_table(self, table): return self.query(f'DROP TABLE IF EXISTS `{table}`') is not None

    def update_table_auto_increment(self, table, start=0):
        return self.query(f'ALTER TABLE {table} AUTO_INCREMENT = {start}') is not None

    def search_table_column_structures(self, table, keyword=None, startwith=None, endwith=None):
        sql = f'SHOW COLUMNS FROM {table}'
        if keyword: sql += f' LIKE "{'' if startwith else '%'}{keyword}{'' if endwith else '%'}";'
        return self.search_table_data_multiple(sql)

    def search_table_columns(self, table, keyword=None, startwith=None, endwith=None):
        return [i['Field'] for i in self.search_table_column_structures(table, keyword, startwith, endwith)]

    def create_table_column(self, table, column, datatype=None, length=0, unique=False, nullable=False):
        datatype = datatype.upper() if datatype and datatype.upper() in self.__si__.DATCOLS else 'varchar'
        sql = f"ALTER TABLE `{table}` ADD `{column}` {datatype}"
        if datatype == 'char' or datatype == 'varchar': sql += f'({length if length else 255})'
        sql += ' NULL' if nullable else ' NOT NULL;'
        result = self.query(sql)
        if result and unique: self.set_table_column_quniue(table, column)
        return result is not None

    def set_table_column_quniue(self, table, column): return self.query(f'ALTER TABLE `{table}` ADD UNIQUE (`{column}`);') is not None

    def search_table_data_multiple(self, sql):
        cursor = self.query(sql)
        if cursor is None: return []
        return list(cursor.fetchall())
