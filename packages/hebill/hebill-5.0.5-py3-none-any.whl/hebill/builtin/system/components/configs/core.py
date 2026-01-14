import inspect
from ..file import File
from ...types.hd import Hd
from ....functions.decorators import parse_self_x_item_value, parse_self_x_item_value_or_set_by_func, \
    parse_self_x_item_value_or_set_by_instance_he_by_module_name
from ...types.he import He


class Configs(Hd):
    def __init__(self, u, data=None, end_class=None, start_class=None, file=None, defaults=None):
        Hd.__init__(self, u)
        if defaults: self.___defaults___.update(defaults)
        original_data = {}
        if file:
            if isinstance(file, File):
                self.__x__['___file___'] = file
            else:
                self.__x__['___file___'] =  self.__sm__.file(file)
                data = self.___file___.parse_json()
                if isinstance(data, dict):
                    self.___defaults___.update(original_data)
        elif end_class:
            start_class = start_class if start_class else He
            if not issubclass(end_class, He): raise RuntimeError('senior_class 必须是继承自 He 的类或者实例')
            if not issubclass(end_class, start_class): raise RuntimeError('end_class 必须是继承自 start_class 的类或者实例')
            self.__x__['___file___'] = self.__sm__.cls_type(end_class).data_configs_file
            for cls in reversed(inspect.getmro(end_class)):
                if not issubclass(cls, start_class): continue
                clstyp = self.__sm__.cls_type(cls)
                if clstyp.data_configs_file.is_exists():
                    data = clstyp.data_configs_file.parse_json()
                    if isinstance(data, dict): self.___defaults___.update(data)
        self.update(self.___defaults___)
        if data: self.update(data)

    @property
    @parse_self_x_item_value_or_set_by_func()
    def ___value_types___(self): return {}

    @property
    @parse_self_x_item_value_or_set_by_func()
    def ___hooks___(self): return {}
    def hook(self, name, target_configs, target_name=None): self.___hooks___[name] = (target_configs, target_name or name)

    @property
    @parse_self_x_item_value_or_set_by_instance_he_by_module_name(module_name_striped=True)
    def ___defaults___(self): return

    def __getitem__(self, name: str):
        if name in self.___hooks___: return self.___hooks___[name][0].__getitem__(self.___hooks___[name][1])
        if name in self: return super().__getitem__(name)
        if name in self.___defaults___: return self.___defaults___[name]
        return None

    def __setitem__(self, name: str, value):
        if name in self.___hooks___: self.___hooks___[name][0].__setitem__(self.___hooks___[name][1], value)
        else:
            if name in self.___value_types___:
                pass
            super().__setitem__(name, value)

    def update(self, m, /, **kwargs):
        if isinstance(m, dict):
            for k, v in m.items(): self.__setitem__(k, v)

    def get(self, name: str): return self.__getitem__(name)
    def set(self, name: str, value): self.__setitem__(name, value)


    @property
    @parse_self_x_item_value()
    def ___file___(self): return

    def save(self):
        if self.___file___:
            self.___file___.save_json(self)
