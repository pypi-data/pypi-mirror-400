from ....types.hd import Hd
from .client import Client
from .. import WebSystem


class Clients(Hd):
    @property
    def __websystem__(self)-> WebSystem: ...
    def get(self, key)-> Client: ...
