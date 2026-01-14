from .......functions.decorators import parse_self_x_item_value, set_self_item_value_by_setter_with_agr
from .....configs import Configs


class Settings(Configs):
    def __init__(self, u):
        super().__init__(u, file=u.data_settings_file, defaults={
            'page_feature': 'general',
            'power': '',
            'icon': 'fa-code',
            'page_layout': '',
        })

    @property
    @parse_self_x_item_value()
    def page_feature(self): return
    @page_feature.setter
    @set_self_item_value_by_setter_with_agr(value_type='str')
    def page_feature(self, value): pass
    def is_page_feature_general(self): return not self.page_feature or self.page_feature == self.__s__.definitions.webapp_page_features.general
    def is_page_feature_sign_in(self): return self.page_feature == self.__s__.definitions.webapp_page_features.sign_in
    def is_page_feature_sign_out(self): return self.page_feature == self.__s__.definitions.webapp_page_features.sign_out
    def is_page_feature_sign_reset(self): return self.page_feature == self.__s__.definitions.webapp_page_features.sign_reset
    def is_page_feature_sign_up(self): return self.page_feature == self.__s__.definitions.webapp_page_features.sign_up

    @property
    @parse_self_x_item_value()
    def power(self): return
    @power.setter
    @set_self_item_value_by_setter_with_agr(value_type='str')
    def power(self, value): pass
    def is_power_public(self): return self.power == self.__s__.definitions.webapp_power_types.public
    def is_power_groups(self): return self.power == self.__s__.definitions.webapp_power_types.groups
    def is_power_inherited(self): return self.power == self.__s__.definitions.webapp_power_types.inherited
    def is_power_members(self): return self.power == self.__s__.definitions.webapp_power_types.members

    @property
    @parse_self_x_item_value()
    def icon(self): return
    @icon.setter
    @set_self_item_value_by_setter_with_agr(value_type='str')
    def icon(self, value): pass

    @property
    @parse_self_x_item_value()
    def page_layout(self): return
    @page_layout.setter
    @set_self_item_value_by_setter_with_agr(value_type='str')
    def page_layout(self, value): pass
