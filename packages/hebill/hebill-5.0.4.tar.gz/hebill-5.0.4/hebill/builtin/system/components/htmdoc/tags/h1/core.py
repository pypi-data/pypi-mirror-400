from ...nodes.tag import Tag


class H1(Tag):
    def __init__(self, u, content=None, attributes:dict[str, str|int|float|None]=None):
        Tag.__init__(self, u, None, content, attributes)
