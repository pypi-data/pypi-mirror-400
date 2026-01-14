from ......functions.decorators import parse_self_x_item_value_or_set_by_instance_he_by_module_name
from ....htmdoc import Htmdoc as PluginHtmDoc


class Htmdoc(PluginHtmDoc):
    def __init__(self, website):
        super().__init__(website)
        self.configs.hook('language', self.__websystem__.configs)
        self.configs.hook('output_minimized', self.__websystem__.configs, 'html_output_minimized')
        self.configs.hook('output_unspaced', self.__websystem__.configs, 'html_output_unspaced')
        self.configs.hook('output_comments', self.__websystem__.configs, 'html_output_comments')
        self.configs.hook('output_indentation', self.__websystem__.configs, 'html_output_indentation')
        self.configs.hook('title_delimiter', self.__websystem__.configs, 'html_title_delimiter')
        self.configs.hook('title_ascending', self.__websystem__.configs, 'html_title_ascending')

    @property
    def __websystem__(self): return self.__website__.websystem
    @property
    def __website__(self): return self.__u__
    @property
    @parse_self_x_item_value_or_set_by_instance_he_by_module_name()
    def areas(self): return

    @property
    @parse_self_x_item_value_or_set_by_instance_he_by_module_name()
    def caches(self): return
