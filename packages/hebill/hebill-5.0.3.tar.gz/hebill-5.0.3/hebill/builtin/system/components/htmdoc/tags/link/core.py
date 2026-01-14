from ...nodes.tag import Tag


class Link(Tag):
    __hd_tag_pairable__ = False
    def __init__(self, u, url=None, attributes:dict[str, str|int|float|None]=None):
        Tag.__init__(self, u, None, None, attributes)
        self.attributes['href'] = url
