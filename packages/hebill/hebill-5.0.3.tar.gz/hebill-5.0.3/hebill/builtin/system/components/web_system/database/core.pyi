from ...database import Database as PluginDatabase
from .. import WebSystem


class Database(PluginDatabase):
    def __init__(self, system: WebSystem): ...
