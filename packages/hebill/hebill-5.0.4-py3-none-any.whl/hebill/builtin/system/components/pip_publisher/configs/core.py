from .....functions.decorators import parse_self_item_value, set_self_item_value_by_setter_with_agr
from ...configs import Configs as PluCfg


class Configs(PluCfg):
    @property
    @parse_self_item_value()
    def version(self): return
    @version.setter
    @set_self_item_value_by_setter_with_agr(value_type='strue')
    def version(self, value): pass

    @property
    @parse_self_item_value()
    def name(self): return
    @name.setter
    @set_self_item_value_by_setter_with_agr(value_type='strue')
    def name(self, value): pass
