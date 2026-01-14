from .....functions.decorators import parse_self_x_item_value, parse_self_x_item_value_or_set_by_func, \
    parse_dict_item_value_or_set_by_instance_he_by_module_name
from ....types.he import He


class Med(He):
    @staticmethod
    def ___make_name___(media_min_width:int=None, media_max_width:int=None, media_min_height:int=None, media_max_height:int=None):
        medias = []
        if media_min_width: medias.append(f'(min-width: {media_min_width}px)')
        if media_max_width: medias.append(f'(max-width: {media_max_width}px)')
        if media_min_height: medias.append(f'(min-height: {media_min_height}px)')
        if media_max_height: medias.append(f'(max-height: {media_max_height}px)')
        return ' and '.join(medias)

    def __init__(self, u, media_min_width:int=None, media_max_width:int=None, media_min_height:int=None, media_max_height:int=None):
        He.__init__(self, u)
        medias = []
        if media_min_width: medias.append(f'(min-width: {media_min_width}px)')
        if media_max_width: medias.append(f'(max-width: {media_max_width}px)')
        if media_min_height: medias.append(f'(min-height: {media_min_height}px)')
        if media_max_height: medias.append(f'(max-height: {media_max_height}px)')
        self.__x__['name'] = ' and '.join(medias)

    @property
    @parse_self_x_item_value()
    def name(self): return

    @property
    @parse_self_x_item_value_or_set_by_func()
    def clses(self): return {}
    @parse_dict_item_value_or_set_by_instance_he_by_module_name(dict_attr_name='clses', dict_item_key_by_arg=0, module_name='.cls')
    def cls(self, name:str): return

    def __str__(self):
        ls = [f'@media {self.name} {{']
        for _, c in self.clses.items():
            ls.append(c.__str__())
        ls.append(f'}}')
        return '\n'.join(ls)
