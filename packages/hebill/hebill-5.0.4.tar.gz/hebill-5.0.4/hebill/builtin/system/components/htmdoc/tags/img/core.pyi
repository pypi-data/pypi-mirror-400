from ... import Htmdoc
from ...nodes.tag import Tag
from ...nodes.wrap import Wrap


class Img(Tag):
    attribute_align_values: list = ...

    def __init__(self, u: Htmdoc | Wrap, url: str = None, width: int = None, height: int = None, title: str = None, attributes:dict[str, str|int|float|None]=None): ...

