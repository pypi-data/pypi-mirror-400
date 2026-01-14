from ..body import Body
from ..head import Head
from ... import Htmdoc
from ...nodes.tag import Tag
from ...nodes.wrap import Wrap


class Html(Tag):
    def __init__(self, u: Htmdoc | Wrap): ...

    @property
    def head(self)-> Head: ...
    @property
    def body(self)-> Body: ...