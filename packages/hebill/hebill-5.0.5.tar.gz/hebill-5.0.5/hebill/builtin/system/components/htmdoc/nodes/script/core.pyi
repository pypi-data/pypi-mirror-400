from ..wrap import Wrap
from ... import Htmdoc
from ...node import Node


class Script(Node):
    def __init__(self, u: Htmdoc | Wrap, content:str=None): ...
    @property
    def content(self)-> str: ...
