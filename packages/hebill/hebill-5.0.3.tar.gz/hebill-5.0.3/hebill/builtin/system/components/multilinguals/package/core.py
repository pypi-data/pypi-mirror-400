from .....functions.decorators import parse_self_x_item_value, parse_self_x_item_value_or_set_by_func
from ....types.hd import Hd


class Package(Hd):
    def __init__(self, multilingual, language):
        super().__init__(multilingual)
        self.__x__['language'] = language
        if self.__u__.___tree_cls_types___:
            for cls_typ in reversed(self.__u__.___tree_cls_types___):
                file = cls_typ.data_multilinguals_file(self.language)
                if file.is_exists():
                    data = file.parse_json()
                    if isinstance(data, dict):
                        self.update(data)
        else:
            if self.file.is_exists():
                data = self.file.parse_json()
                if isinstance(data, dict):
                    self.update(data)

    @property
    @parse_self_x_item_value()
    def language(self): return

    @property
    @parse_self_x_item_value_or_set_by_func()
    def file(self): return self.__u__.folder.child_file(f'{self.language}.json')

    def load(self): self.update(self.file.parse_json())

    def read(self, code): return self.get(code)

    def ml(self, code, replace=None, return_code=False):
        return self.read(code) or replace or (code if return_code else None)

    def save(self, code, traslation=None):
        if isinstance(code, str) and traslation is not None:
            self[code] = traslation
        elif isinstance(code, dict):
            self.update(code)
        self.file.save_json(self)
