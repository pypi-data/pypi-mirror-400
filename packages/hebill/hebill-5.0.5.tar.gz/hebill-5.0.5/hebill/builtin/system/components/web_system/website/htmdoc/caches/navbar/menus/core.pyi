from .menu import Menu
from .dropdown import Dropdown


class Menus(list):
    def add_menu(self, title, url=None)-> Menu: ...
    def add_dropdown(self, title)-> Dropdown: ...
