from .....multilinguals import Multilinguals as ModMultilinguals
from .. import Webmod


class Multilinguals(ModMultilinguals):
    def __init__(self, u: Webmod): ...
    @property
    def __u__(self)-> Webmod: ...
