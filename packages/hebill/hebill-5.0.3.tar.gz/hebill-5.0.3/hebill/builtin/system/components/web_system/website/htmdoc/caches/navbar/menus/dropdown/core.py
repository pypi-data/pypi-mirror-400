from .menus import Menus


class Dropdown(dict):
    def __init__(self, title=None):
        dict.__init__(self)
        self.update({
            'title': title,
            'menus': Menus(self),
        })

    @property
    def title(self): return self.get('title')
    @title.setter
    def title(self, value): self['title'] = value

    @property
    def menus(self): return self.get('menus')

    def is_menu(self): return False
    def is_dropdown(self): return True