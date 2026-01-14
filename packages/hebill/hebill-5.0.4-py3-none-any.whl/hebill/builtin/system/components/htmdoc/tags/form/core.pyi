from ... import Htmdoc
from ...nodes.tag import Tag
from ...nodes.wrap import Wrap


class Form(Tag):
    def __init__(self, u: Htmdoc | Wrap, action: str = None, attributes:dict[str, str|int|float|None]=None): ...
