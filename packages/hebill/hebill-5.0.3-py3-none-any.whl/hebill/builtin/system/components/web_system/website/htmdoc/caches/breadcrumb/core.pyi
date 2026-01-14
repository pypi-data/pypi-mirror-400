from .menu import Menu


class Breadcrumb(list):
    def add_menu(self, title, url=None)-> Menu: ...
