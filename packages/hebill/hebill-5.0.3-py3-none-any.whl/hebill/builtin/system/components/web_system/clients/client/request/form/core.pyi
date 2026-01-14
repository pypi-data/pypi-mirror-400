from ..... import WebSystem
from .......types.hd import Hd
from .....configs import Configs
from .....clients import Clients
from ... import Client
from .. import Request


class Form(Hd):
    @property
    def __websystem__(self)-> WebSystem: ...
    @property
    def __clients__(self)-> Clients: ...
    @property
    def __client__(self)-> Client: ...
    @property
    def __request__(self)-> Request: ...
    @property
    def __configs__(self)-> Configs: ...
