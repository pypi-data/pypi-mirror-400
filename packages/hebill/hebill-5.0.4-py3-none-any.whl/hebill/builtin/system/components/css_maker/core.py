from ..file import File
from ....functions.decorators import set_self_item_value_by_setter_with_agr, \
    parse_self_x_item_value_or_set_by_func, parse_dict_item_value_or_set_by_instance_he_by_module_name, \
    parse_self_x_item_value
from ...types.he import He


class CssMaker(He):
    def __init__(self, u, file: str | File = None, version=None):
        He.__init__(self, u)
        self.__x__['file'] = file if isinstance(file, File) else self.__sm__.file(file) if file else None
        self.__x__['version'] = version or '1.0.0'
    @property
    @parse_self_x_item_value()
    def file(self): return
    @property
    @parse_self_x_item_value()
    def version(self): return

    @property
    @parse_self_x_item_value_or_set_by_func()
    def sizes(self): return []
    @sizes.setter
    @set_self_item_value_by_setter_with_agr(value_type='lst')
    def sizes(self, value): return

    @property
    def cls_root(self): return self.cls(':root')
    @property
    def css_html(self): return self.cls('html')
    @property
    def css_body(self): return self.cls('body')

    @property
    @parse_self_x_item_value_or_set_by_func()
    def clses(self): return {}
    @parse_dict_item_value_or_set_by_instance_he_by_module_name(dict_attr_name='clses', dict_item_key_by_arg=0)
    def cls(self, name:str): return

    @property
    @parse_self_x_item_value_or_set_by_func()
    def medes(self): return {}
    @parse_dict_item_value_or_set_by_instance_he_by_module_name(dict_attr_name='clses', dict_item_key_by_func=True)
    def med(self, media_min_width:int=None, media_max_width:int=None, media_min_height:int=None, media_max_height:int=None):
        from .med import Med
        return Med.___make_name___(media_min_width, media_max_width, media_min_height, media_max_height)


    def save(self, minimized: bool = None):
        # fm = f.parent.child_file(f'min-{f.name}')
        rs = str(self)
        # rm = rs.replace('\n', '').replace('\t', '')
        if self.file:
            self.file.save_content(rs)
            if minimized:
                self.file.brother_file(f'{self.file.base_name}-min.css').save_content(rs.replace('\n', '').replace('\t', ''))
        else:
            print(rs)

    def __str__(self):
        ls = [
            f'/*!',
            f' * Hebill v{self.version}',
            f' * 版权所有 / Copyright 2026-2027 ©Hebill.',
            f' * 本作品仅限非商业用途使用，禁止商业行为。 / You may not use this work for commercial purposes.',
            f'*/',
        ]
        for n, c in self.medes.items():
            ls.append(c.__str__())
        for n, c in self.clses.items():
            ls.append(c.__str__())
        return '\n'.join(ls)
