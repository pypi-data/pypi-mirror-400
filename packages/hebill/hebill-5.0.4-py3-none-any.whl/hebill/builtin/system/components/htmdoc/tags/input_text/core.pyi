from ... import Htmdoc
from ..input import Input
from ...nodes.wrap import Wrap


class InputText(Input):
    def __init__(self, u: Htmdoc | Wrap, name: str = None, value: str = None, placeholder:str=None, attributes: dict=None): ...
