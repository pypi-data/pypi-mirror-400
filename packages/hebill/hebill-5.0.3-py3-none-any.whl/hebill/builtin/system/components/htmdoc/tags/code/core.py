from ...nodes.tag import Tag


class Code(Tag):
    def __init__(self, u, content:str=None, attributes:dict[str, str|int|float|None]=None):
        Tag.__init__(self, u, None, attributes)
