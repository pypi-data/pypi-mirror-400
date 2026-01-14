from .......types.hd import Hd


class Arguments(Hd):
    @property
    def __websystem__(self): return self.__clients__.__websystem__
    @property
    def __clients__(self): return self.__client__.__clients__
    @property
    def __client__(self): return self.__request__.__client__
    @property
    def __request__(self): return self.__u__
    @property
    def __configs__(self): return self.__websystem__.configs

    def __getitem__(self, item): return super().__getitem__(item) if item in self else ''
