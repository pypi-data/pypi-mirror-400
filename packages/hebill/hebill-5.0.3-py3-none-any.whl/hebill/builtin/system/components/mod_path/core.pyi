from types import ModuleType

from ..cls_type import ClsType
from ..mod_type import ModType
from ...types.he import He
from ...types.hs import Hs


class ModPath(Hs):
    def __init__(self, u: He, name: str | ModuleType | type | He): ...

    @property
    def pymod(self)-> ModuleType | None: ...
    @property
    def pycls(self)-> type | None: ...

    @property
    def mod_type(self)-> ModType | None: ...
    @property
    def cls_type(self)-> ClsType | None: ...

    def rel_mod_path(self, relname: str = None)-> ModPath: ...
