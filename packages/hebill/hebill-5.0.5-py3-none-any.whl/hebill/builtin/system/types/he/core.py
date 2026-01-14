from ....functions.decorators import parse_self_x_item_value, parse_self_x_item_value_or_set_by_func, \
    parse_self_x_item_value_or_set_by_instance_he_by_module_name


class He:
    def __init__(self, u):
        self.__x = {}
        from ....system import System
        if isinstance(u, System):
            self.__x__['__s__'] = u
            self.__x__['__u__'] = None
        elif isinstance(u, He):
            self.__x__['__s__'] = u.__s__
            self.__x__['__u__'] = u
        else:
            raise TypeError(f'{type(u)} 不是 System | He。')

    @property
    @parse_self_x_item_value_or_set_by_instance_he_by_module_name(module_name_striped=True)
    def __i__(self): return
    @property
    def __id__(self): return id(self)
    @property
    def __x__(self): return self.__x

    @property
    @parse_self_x_item_value()
    def __s__(self): return
    @property
    def __sm__(self): return self.__s__.components
    @property
    def __sc__(self): return self.__s__.configs
    @property
    def __sd__(self): return self.__s__.debugs
    @property
    def __si__(self): return self.__s__.__i__
    @property
    def __st__(self): return self.__s__.types

    @property
    @parse_self_x_item_value()
    def __u__(self): return

    @property
    @parse_self_x_item_value_or_set_by_func()
    def __l__(self): return []

    @property
    @parse_self_x_item_value_or_set_by_func()
    def __d__(self): return {}

    @property
    @parse_self_x_item_value_or_set_by_func()
    def __t__(self): return ''
