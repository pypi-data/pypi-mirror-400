from ..he import He


class Hl(He, list):
    def __init__(self, u, data: list=None):
        He.__init__(self, u)
        list.__init__(self)
        if data: self.extend(data)
