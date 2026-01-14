from .......functions.decorators import parse_self_x_item_value_or_set_by_func
from ......types.hd import Hd


class Caches(Hd):
    @property
    @parse_self_x_item_value_or_set_by_func()
    def breadcrumb(self): from .breadcrumb import Breadcrumb; return Breadcrumb()
    @property
    @parse_self_x_item_value_or_set_by_func()
    def navbar(self): from .navbar import Navbar; return Navbar()
