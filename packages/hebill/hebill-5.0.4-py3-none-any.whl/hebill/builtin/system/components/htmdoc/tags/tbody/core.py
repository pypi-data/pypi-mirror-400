from ...nodes.tag import Tag


class Tbody(Tag):
    def __init__(self, u, attributes:dict[str, str|int|float|None]=None):
        Tag.__init__(self, u, None, attributes)
