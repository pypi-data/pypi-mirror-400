from ......functions.decorators import parse_self_x_item_value
from ..wrap import Wrap


class Tag(Wrap):
    def __init__(self, u, name=None, content=None, attributes:dict[str, str|int|float|None]=None):
        Wrap.__init__(self, u, content)
        self.attributes.update(attributes or {})
        if name: self.___name___ = name
        else:
            mro = type(self).__mro__
            self.___name___ = mro[mro.index(Tag) - 1].__name__.lower()


    @staticmethod
    def is_wrap(): return False
    @staticmethod
    def is_tag(): return True

    @property
    def name(self): return self.___name___

    @property
    def attributes(self): return self.___attributes___

    def inner_before(self, sn:int): return self.___inner_before___(sn)
    @property
    def inner_before1(self): return self.___anchor___(1)
    @property
    def inner_before2(self): return self.___anchor___(2)
    @property
    def inner_before3(self): return self.___anchor___(3)
    @property
    def inner_before4(self): return self.___anchor___(4)
    @property
    def inner_before5(self): return self.___anchor___(5)
    def inner_after(self, sn:int):  return self.___inner_after___(sn)
    @property
    def inner_after1(self): return self.___anchor___(-1)
    @property
    def inner_after2(self): return self.___anchor___(-2)
    @property
    def inner_after3(self): return self.___anchor___(-3)
    @property
    def inner_after4(self): return self.___anchor___(-4)
    @property
    def inner_after5(self): return self.___anchor___(-5)

    @property
    @parse_self_x_item_value()
    def output_pairable(self): return
    @property
    @parse_self_x_item_value()
    def output_brealable(self): return
