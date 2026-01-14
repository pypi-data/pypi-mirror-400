from .menus import Menus
from .menus.menu import Menu
from .menus.dropdown.core import Dropdown


class Navbar(dict):

    @property
    def logo(self)-> str: ...
    @logo.setter
    def logo(self, value): ...

    @property
    def title(self): ...
    @title.setter
    def title(self, value): ...

    @property
    def menus(self)-> Menus | list[Menu | Dropdown]: ...
