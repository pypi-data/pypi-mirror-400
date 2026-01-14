from .....functions.decorators import parse_self_x_item_value_or_set_by_func
from ....types.he import He


class Connection(He):

    def is_connected(self, recheck=False): return

    @property
    @parse_self_x_item_value_or_set_by_func()
    def queried_sqls(self): return []
    @property
    def last_queried_sql(self): return self.queried_sqls[-1] if len(self.queried_sqls) > 0 else ''
    @property
    @parse_self_x_item_value_or_set_by_func()
    def queried_times(self): return len(self.queried_sqls)

    def query(self, sql): return

    # noinspection PyMethodMayBeStatic
    def search_tables(self, keyword=None, startwith=None, endwith=None): raise RuntimeError('函数必须在继承类中重写')

    def is_table_exists(self, table): return table in self.search_tables()

    def create_table(self, table): raise RuntimeError('函数必须在继承类中重写')
    def delete_table(self, table): raise RuntimeError('函数必须在继承类中重写')

    def search_table_column_structures(self, table, keyword=None, startwith=None, endwith=None): raise RuntimeError('函数必须在继承类中重写')
    def search_table_columns(self, table, keyword=None, startwith=None, endwith=None): raise RuntimeError('函数必须在继承类中重写')

    def create_table_column(self, table, column, datatype=None, length=0, unique=False, nullable=False): raise RuntimeError('函数必须在继承类中重写') 
    def set_table_column_quniue(self, table, column): raise RuntimeError('函数必须在继承类中重写')

    def search_table_data_multiple(self, sql): raise RuntimeError('函数必须在继承类中重写')
