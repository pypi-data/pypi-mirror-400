from ...nodes.tag import Tag


class Th(Tag):
    def __init__(self, u, content=None, colspan:int=None, rowspan:int=None, attributes:dict[str, str|int|float|None]=None):
        Tag.__init__(self, u, None, content, attributes)
        if colspan: self.attributes.setdefault('colspan', colspan)
        if rowspan: self.attributes.setdefault('rowspan', rowspan)
