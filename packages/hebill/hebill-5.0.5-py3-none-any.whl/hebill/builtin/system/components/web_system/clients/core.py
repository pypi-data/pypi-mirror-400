from ....types.hd import Hd
from .client import Client


class Clients(Hd):
    def __getitem__(self, key):
        if key not in self:
            self[key] = Client(self, key)
        return super().__getitem__(key)

    @property
    def __websystem__(self): return self.__u__

    def get(self, key): return self.__getitem__(key)
