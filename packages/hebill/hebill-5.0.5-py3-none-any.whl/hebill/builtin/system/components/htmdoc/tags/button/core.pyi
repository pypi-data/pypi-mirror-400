from ... import Htmdoc
from ...nodes.tag import Tag
from ...nodes.wrap import Wrap


class Button(Tag):
    def __init__(self, u: Htmdoc | Wrap, title=None, attributes:dict[str, str|int|float|None]=None): ...
