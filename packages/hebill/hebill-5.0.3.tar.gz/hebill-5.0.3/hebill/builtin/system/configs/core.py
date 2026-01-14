from ..components.configs import Configs as ModConfigs
from ...functions.decorators import parse_self_item_value, set_self_item_value_by_setter_with_agr


class Configs(ModConfigs):
    def __init__(self, s):
      super().__init__(s, None, s.__class__, s.__class__)

    @property
    @parse_self_item_value()
    def language(self): return
    @language.setter
    @set_self_item_value_by_setter_with_agr(value_type='lan')
    def language(self, value): pass

    @property
    @parse_self_item_value()
    def debug_prefix(self): return
    @debug_prefix.setter
    @set_self_item_value_by_setter_with_agr(value_type='str')
    def debug_prefix(self, value): pass

    @property
    @parse_self_item_value()
    def debug_printable(self): return
    @debug_printable.setter
    @set_self_item_value_by_setter_with_agr(value_type='bol')
    def debug_printable(self, value): pass

    @property
    @parse_self_item_value()
    def debug_saveable(self): return
    @debug_saveable.setter
    @set_self_item_value_by_setter_with_agr(value_type='bol')
    def debug_saveable(self, value): pass
