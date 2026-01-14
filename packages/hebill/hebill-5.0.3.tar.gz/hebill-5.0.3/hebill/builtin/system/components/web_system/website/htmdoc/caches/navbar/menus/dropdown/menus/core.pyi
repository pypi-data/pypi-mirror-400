from .menu import Menu


class Menus(list):
    def add_menu(self, title, url=None)-> Menu: ...
