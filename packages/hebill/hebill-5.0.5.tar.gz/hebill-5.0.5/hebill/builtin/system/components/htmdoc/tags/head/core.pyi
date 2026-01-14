from ..title import Title
from ... import Htmdoc
from ...nodes.tag import Tag
from ...nodes.wrap import Wrap


class Head(Tag):
    def __init__(self, u: Htmdoc | Wrap, attributes:dict[str, str|int|float|None]=None): ...
    @property
    def title(self)-> Title: ...


