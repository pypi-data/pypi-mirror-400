from .menu import Menu
from .dropdown import Dropdown


class Menus(list):
    def add_menu(self, title, url=None):
        menu = Menu(title, url)
        self.append(menu)
        return menu

    def add_dropdown(self, title):
        dropdown = Dropdown(title)
        self.append(dropdown)
        return dropdown
