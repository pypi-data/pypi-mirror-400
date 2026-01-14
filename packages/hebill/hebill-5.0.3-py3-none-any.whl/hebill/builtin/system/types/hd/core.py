from ..he import He


class Hd(He, dict):
    def __init__(self, u, data: dict=None):
        He.__init__(self, u)
        dict.__init__(self)
        if data: self.update(data)

    def __ds__(self, name, value): self[name] = value

    def __getitem__(self, name: str):
        return super().__getitem__(name) if name in self else None

    def get(self, name):
        return self.__getitem__(name)
