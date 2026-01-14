from .....functions.decorators import set_self_item_value_by_setter_with_agr, parse_self_item_value
from ...configs import Configs as ModConfigs
from ....types.he import He


class Configs(ModConfigs):
    def __init__(self, u: He):
        super().__init__(u, {
            "connection": "mysql",

            "host": "",
            "port": 3306,
            "user": "",
            "password": "",
            "dbname": "",
            "prefix": "",

            "max_connections": 30,
            "connect_timeout": 5,
            "column_key_sn": "_sn",
            "column_key_id": "_id",
            "column_key_az": "_az",
            "column_key_kw": "_kw",
            "column_key_ur": "_ur",
            "column_key_dc": "_dc",
            "column_key_du": "_du",
            "data_admin_id": "_admin",
        })

    @property
    @parse_self_item_value()
    def connection(self): return
    @connection.setter
    @set_self_item_value_by_setter_with_agr(value_type='strue')
    def connection(self, value): pass
    @property
    @parse_self_item_value()
    def host(self): return
    @host.setter
    @set_self_item_value_by_setter_with_agr(value_type='strue')
    def host(self, value): pass
    @property
    @parse_self_item_value()
    def port(self): return
    @port.setter
    @set_self_item_value_by_setter_with_agr(value_type='intp')
    def port(self, value): pass
    @property
    @parse_self_item_value()
    def user(self): return
    @user.setter
    @set_self_item_value_by_setter_with_agr(value_type='strue')
    def user(self, value): pass
    @property
    @parse_self_item_value()
    def password(self): return
    @password.setter
    @set_self_item_value_by_setter_with_agr(value_type='strue')
    def password(self, value): pass
    @property
    @parse_self_item_value()
    def dbname(self): return
    @dbname.setter
    @set_self_item_value_by_setter_with_agr(value_type='strue')
    def dbname(self, value): pass
    @property
    @parse_self_item_value()
    def prefix(self): return
    @prefix.setter
    @set_self_item_value_by_setter_with_agr(value_type='strue')
    def prefix(self, value): pass
    @property
    @parse_self_item_value()
    def max_connections(self): return
    @max_connections.setter
    @set_self_item_value_by_setter_with_agr(value_type='intp')
    def max_connections(self, value): pass
    @property
    @parse_self_item_value()
    def connect_timeout(self): return
    @connect_timeout.setter
    @set_self_item_value_by_setter_with_agr(value_type='intp')
    def connect_timeout(self, value): pass
    @property
    @parse_self_item_value()
    def column_key_sn(self): return
    @column_key_sn.setter
    @set_self_item_value_by_setter_with_agr(value_type='strue')
    def column_key_sn(self, value): pass
    @property
    @parse_self_item_value()
    def column_key_id(self): return
    @column_key_id.setter
    @set_self_item_value_by_setter_with_agr(value_type='strue')
    def column_key_id(self, value): pass
    @property
    @parse_self_item_value()
    def column_key_az(self): return
    @column_key_az.setter
    @set_self_item_value_by_setter_with_agr(value_type='strue')
    def column_key_az(self, value): pass
    @property
    @parse_self_item_value()
    def column_key_kw(self): return
    @column_key_kw.setter
    @set_self_item_value_by_setter_with_agr(value_type='strue')
    def column_key_kw(self, value): pass
    @property
    @parse_self_item_value()
    def column_key_ur(self): return
    @column_key_ur.setter
    @set_self_item_value_by_setter_with_agr(value_type='strue')
    def column_key_ur(self, value): pass
    @property
    @parse_self_item_value()
    def column_key_dc(self): return
    @column_key_dc.setter
    @set_self_item_value_by_setter_with_agr(value_type='strue')
    def column_key_dc(self, value): pass
    @property
    @parse_self_item_value()
    def column_key_du(self): return
    @column_key_du.setter
    @set_self_item_value_by_setter_with_agr(value_type='strue')
    def column_key_du(self, value): pass
    @property
    @parse_self_item_value()
    def data_admin_id(self): return
    @data_admin_id.setter
    @set_self_item_value_by_setter_with_agr(value_type='strue')
    def data_admin_id(self, value): pass
