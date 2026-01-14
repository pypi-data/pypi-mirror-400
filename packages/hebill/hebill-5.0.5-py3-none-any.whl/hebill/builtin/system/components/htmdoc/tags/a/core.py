from ...nodes.tag import Tag


class A(Tag):
    def __init__(self, u, title=None, url:str = None, attributes:dict[str, str|int|float|None]=None):
        (attributes := attributes or {})['href'] = url
        Tag.__init__(self, u, None, title, attributes)
