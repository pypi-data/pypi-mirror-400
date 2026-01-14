from ...nodes.tag import Tag


class Hr(Tag):
    __hd_tag_pairable__ = False
    def __init__(self, u, attributes:dict[str, str|int|float|None]=None):
        Tag.__init__(self, u, None, attributes)
