from ....functions.decorators import parse_self_x_item_value_or_set_by_instance_he_by_module_name, \
    parse_self_x_item_value_or_set_by_func
from ...types.he import He


class Debugs(He):
    @property
    @parse_self_x_item_value_or_set_by_instance_he_by_module_name(search_from_self=True)
    def configs(self): return

    @property
    @parse_self_x_item_value_or_set_by_instance_he_by_module_name(search_from_self=True)
    def input(self): return

    @property
    @parse_self_x_item_value_or_set_by_instance_he_by_module_name(search_from_self=True)
    def output(self): return

    @property
    @parse_self_x_item_value_or_set_by_func()
    def ___prefixes___(self): return []

    @property
    def prefixes(self): return [self.configs.prefix, *self.___prefixes___] if self.configs.prefix else self.___prefixes___

    def add_prefix(self, prefix):
        if prefix :self.___prefixes___.append(prefix)

    def make_prefix(self, prefix):
        prefixes = []
        if self.configs.prefix: prefixes.append(self.configs.prefix)
        if isinstance(prefix, str) and prefix:prefixes.append(prefix)
        elif isinstance(prefix, list | tuple): prefixes.extend([i for i in prefix if i])
        if self.configs.prefix and self.___prefixes___: return '/'.join(f'[{i}]' for i in prefixes) + '/:>'
        return '[HEBILL]/:>'
