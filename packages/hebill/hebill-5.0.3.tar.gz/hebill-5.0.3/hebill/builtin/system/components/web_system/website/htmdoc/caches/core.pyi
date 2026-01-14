from .navbar import Navbar
from ......types.hd import Hd
from .breadcrumb import Breadcrumb


class Caches(Hd):

    @property
    def breadcrumb(self)-> Breadcrumb: ...
    @property
    def navbar(self)-> Navbar: ...
