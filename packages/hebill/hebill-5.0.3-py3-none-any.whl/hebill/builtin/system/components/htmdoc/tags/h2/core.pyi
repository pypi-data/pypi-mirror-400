from ... import Htmdoc
from ...nodes.tag import Tag
from ...nodes.wrap import Wrap


class H2(Tag):
    def __init__(self, u: Htmdoc | Wrap, content=None, attributes:dict[str, str|int|float|None]=None): ...
