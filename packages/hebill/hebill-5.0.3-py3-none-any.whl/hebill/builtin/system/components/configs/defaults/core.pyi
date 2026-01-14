from .. import Configs
from ....types.hd import Hd


class Defaults(Hd):
    @property
    def __u__(self)-> Configs: ...
    def __getitem__(self, name: str): ...