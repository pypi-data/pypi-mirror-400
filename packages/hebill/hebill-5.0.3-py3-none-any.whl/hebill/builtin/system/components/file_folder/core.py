import os
from ....functions.decorators import parse_self_x_item_value_or_set_by_func
from ...types.hs import Hs


class FileFolder(Hs):
    def __init__(self, u, path: str):
        super().__init__(u, path)

    @property
    def name(self): return os.path.basename(self)

    @property
    @parse_self_x_item_value_or_set_by_func()
    def parent(self): return self.__sm__.folder(os.path.dirname(self))
    def brother_file(self, name): return self.parent.child_file(name)
    def brother_folder(self, name): return self.parent.child_folder(name)
