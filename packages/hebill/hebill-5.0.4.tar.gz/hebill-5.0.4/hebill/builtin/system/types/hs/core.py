from ..he import He


class Hs(He, str):
    def __new__(cls, u, string: str):
        obj = str.__new__(cls, string)
        obj.u = u
        return obj

    def __init__(self, u, string: str):
        He.__init__(self, u)
