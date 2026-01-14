from .menus import Menus


class Navbar(dict):
    def __init__(self):
        super().__init__()
        self.update({
            'logo': '',
            'title': '',
            'menus': Menus(),
        })

    @property
    def logo(self): return self.get('logo')
    @logo.setter
    def logo(self, value): self['logo'] = value

    @property
    def title(self): return self.get('title')
    @title.setter
    def title(self, value): self['title'] = value

    @property
    def menus(self): return self.get('menus')