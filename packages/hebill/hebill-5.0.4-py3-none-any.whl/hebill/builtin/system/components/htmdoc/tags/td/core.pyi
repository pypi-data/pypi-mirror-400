from ... import Htmdoc
from ...nodes.tag import Tag
from ...nodes.wrap import Wrap


class Td(Tag):
    def __init__(self, u: Htmdoc | Wrap, content=None, colspan:int=None, rowspan:int=None, attributes:dict[str, str|int|float|None]=None): ...
