from ... import Htmdoc
from ...nodes.tag import Tag
from ...nodes.wrap import Wrap


class Input(Tag):
    def __init__(self, u: Htmdoc | Wrap, name: str = None, value: str = None, attributes:dict[str, str|int|float|None]=None): ...
