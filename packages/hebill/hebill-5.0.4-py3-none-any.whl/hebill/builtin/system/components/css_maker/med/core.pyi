from ..cls import Cls
from ..core import CssMaker
from ....types.he import He


class Med(He):
    @staticmethod
    def ___make_name___(media_min_width:int=None, media_max_width:int=None, media_min_height:int=None, media_max_height:int=None)->str: ...

    def __init__(self, u, name: str, media_min_width:int=None, media_max_width:int=None, media_min_height:int=None, media_max_height:int=None): ...

    @property
    def __u__(self)-> CssMaker: ...

    @property
    def name(self)-> str: ...

    @property
    def clses(self)-> dict[str, Cls]: ...
    def cls(self, name:str)-> Cls: ...
