from .....functions.decorators import set_self_item_value_by_setter_with_agr, parse_self_item_value
from ...configs import Configs as ModConfigs


class Configs(ModConfigs):
    def __init__(self, u):
        super().__init__(u, {
            'language': 'gb',
            'output_minimized': False,
            'output_unspaced': False,
            'output_comments': True,
            'output_indentation': '\t',
            'title_delimiter': '>',
            'title_ascending': True,
        })

    @property
    @parse_self_item_value()
    def language(self): return
    @language.setter
    @set_self_item_value_by_setter_with_agr(value_type='lan')
    def language(self, value): pass

    @property
    @parse_self_item_value()
    def output_minimized(self): return
    @output_minimized.setter
    @set_self_item_value_by_setter_with_agr(value_type='bol')
    def output_minimized(self, value): pass

    @property
    @parse_self_item_value()
    def output_unspaced(self): return
    @output_unspaced.setter
    @set_self_item_value_by_setter_with_agr(value_type='bol')
    def output_unspaced(self, value): pass

    @property
    @parse_self_item_value()
    def output_comments(self): return
    @output_comments.setter
    @set_self_item_value_by_setter_with_agr(value_type='bol')
    def output_comments(self, value): pass

    @property
    @parse_self_item_value()
    def output_indentation(self): return
    @output_indentation.setter
    @set_self_item_value_by_setter_with_agr(value_type='str')
    def output_indentation(self, value): pass

    @property
    @parse_self_item_value()
    def title_delimiter(self): return
    @title_delimiter.setter
    @set_self_item_value_by_setter_with_agr(value_type='str')
    def title_delimiter(self, value): pass

    @property
    @parse_self_item_value()
    def title_ascending(self): return
    @title_ascending.setter
    @set_self_item_value_by_setter_with_agr(value_type='bol')
    def title_ascending(self, value): pass
