from ... import Htmdoc
from ...nodes.code import Code
from ...nodes.tag import Tag
from ...nodes.wrap import Wrap


class Script(Tag):
    def __init__(self, u: Htmdoc | Wrap, code: str = None, attributes:dict[str, str|int|float|None]=None): ...
    @property
    def content(self)-> Code: ...
