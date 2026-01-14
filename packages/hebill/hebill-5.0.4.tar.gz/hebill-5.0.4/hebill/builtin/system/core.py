import os

from .types.he import He
from ..functions.decorators import parse_self_x_item_value_or_set_by_instance_he_by_module_name


class System(He):
    def __init__(self):
        He.__init__(self, self)

    @property
    @parse_self_x_item_value_or_set_by_instance_he_by_module_name()
    def components(self): return

    @property
    @parse_self_x_item_value_or_set_by_instance_he_by_module_name()
    def configs(self): return

    @property
    @parse_self_x_item_value_or_set_by_instance_he_by_module_name()
    def debugs(self): return

    @property
    @parse_self_x_item_value_or_set_by_instance_he_by_module_name()
    def types(self): return

    def initialize_website(self, name:str=None): self.__i__.website_folder.copyto(self.__i__.working_folder.child_folder(name or 'website'))
