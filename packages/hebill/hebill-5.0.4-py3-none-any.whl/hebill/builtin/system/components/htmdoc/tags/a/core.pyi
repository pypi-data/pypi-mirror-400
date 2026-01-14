from ... import Htmdoc
from ...nodes.tag import Tag
from ...nodes.wrap import Wrap


class A(Tag):
    def __init__(self, u: Htmdoc | Wrap): ...
