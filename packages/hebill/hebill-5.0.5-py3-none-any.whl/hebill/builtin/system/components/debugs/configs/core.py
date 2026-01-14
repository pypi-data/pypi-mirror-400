from .....functions.decorators import parse_self_item_value, set_self_item_value_by_setter_with_agr
from ...configs import Configs as PluCfg


class Configs(PluCfg):
    def __init__(self, u):
        PluCfg.__init__(self, u, {
            'prefix': 'Dubeg',
            'printable': True,
            'saveable': False,
        })
    @property
    @parse_self_item_value()
    def prefix(self): return
    @prefix.setter
    @set_self_item_value_by_setter_with_agr(value_type='str')
    def prefix(self, value: str): pass
    @property
    @parse_self_item_value()
    def printable(self): return
    @printable.setter
    @set_self_item_value_by_setter_with_agr(value_type='bol')
    def printable(self, value: str): pass
    @property
    @parse_self_item_value()
    def saveable(self): return
    @saveable.setter
    @set_self_item_value_by_setter_with_agr(value_type='bol')
    def saveable(self, value: str): pass
