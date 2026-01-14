from ....types.hd import Hd


class Defaults(Hd):
    def __getitem__(self, name: str, default=None):
        if name in self.__u__.___hooks___: return self.__u__.___hooks___[name][0].___defaults___.__getitem__(name)
        if name in self: return super().__getitem__(name)
        return None