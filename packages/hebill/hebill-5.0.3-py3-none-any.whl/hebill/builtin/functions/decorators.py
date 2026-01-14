from .builtins import HeEro


def _dict(self, dict_attr_name, es):
    if dict_attr_name: d = getattr(self, dict_attr_name)
    else: d = self
    if not isinstance(d, dict): raise es.add(f'解析字典得到的属性（{type(d)}）没有继承 dict')
    return d
def _key(self, func, args, kwargs, dict_item_key, dict_item_key_by_arg, dict_item_key_by_func, func_name_striped, es):
    if isinstance(dict_item_key_by_arg, str):
        if dict_item_key_by_arg not in kwargs: raise es.add(f'解析字典键名 dict_item_key_by_arg[{dict_item_key_by_arg}] 未在 kwargs 设定')
        return kwargs[dict_item_key_by_arg]
    if isinstance(dict_item_key_by_arg, int):
        if dict_item_key_by_arg not in range(len(args)): raise es.add(f'解析字典键名 dict_item_key_by_arg[{dict_item_key_by_arg}] 超出了 len(args)[{len(args)}] 的范围')
        return args[dict_item_key_by_arg]
    if dict_item_key_by_func:
        return func(self, *args, **kwargs)
    if dict_item_key is not None:
        return dict_item_key
    if func_name_striped:
        return func.__name__.strip('_')
    return func.__name__
def parse_dict_item_value(dict_attr_name: str = None, dict_item_key: str = None, dict_item_key_by_arg: str | int = None, func_name_striped: bool = None):
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            es = HeEro(self, func, f'直接获取字典值', 'parse_dict_item_value', {'dict_attr_name': dict_attr_name, 'dict_item_key': dict_item_key, 'dict_item_key_by_arg': dict_item_key_by_arg, 'func_name_striped': func_name_striped})
            d, k = _dict(self, dict_attr_name, es), _key(self, func, args, kwargs, dict_item_key, dict_item_key_by_arg, False, func_name_striped, es)
            # print(type(self), dict_attr_name)
            if k in d: return d[k]
            return None
        return wrapper
    return decorator
def parse_self_item_value(dict_item_key: str | int = None, dict_item_key_by_arg: str | int = None, func_name_striped: bool = None): return parse_dict_item_value(None, dict_item_key, dict_item_key_by_arg, func_name_striped)
def parse_self_x_item_value(dict_item_key: str | int = None, dict_item_key_by_arg: str | int = None, func_name_striped: bool = None): return parse_dict_item_value('__x__', dict_item_key, dict_item_key_by_arg, func_name_striped)
def parse_self_d_item_value(dict_item_key: str | int = None, dict_item_key_by_arg: str | int = None, func_name_striped: bool = None): return parse_dict_item_value('__d__', dict_item_key, dict_item_key_by_arg, func_name_striped)
def parse_dict_item_value_or_set_by_func(dict_attr_name: str = None, dict_item_key: str = None, dict_item_key_by_arg: str | int = None, func_name_striped: bool = None, execute_if_none: bool = None):
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            es = HeEro(self, func, f'获取字典值，如果没有则运行函数赋值并返回', 'parse_dict_item_value_or_set_by_func', {'dict_attr_name': dict_attr_name, 'dict_item_key': dict_item_key, 'dict_item_key_by_arg': dict_item_key_by_arg, 'execute_if_none': func_name_striped, 'func_name_striped': execute_if_none})
            d, k = _dict(self, dict_attr_name, es), _key(self, func, args, kwargs, dict_item_key, dict_item_key_by_arg, False, func_name_striped, es)
            if k not in d or (d[k] is None and execute_if_none): d[k] = func(self, *args, **kwargs)
            return d[k]
        return wrapper
    return decorator
def parse_self_item_value_or_set_by_func(dict_item_key: str = None, dict_item_key_by_arg: str | int = None, func_name_striped: bool = None, execute_if_none: bool = None): return parse_dict_item_value_or_set_by_func(None, dict_item_key, dict_item_key_by_arg, func_name_striped, execute_if_none)
def parse_self_x_item_value_or_set_by_func(dict_item_key: str = None, dict_item_key_by_arg: str | int = None, func_name_striped: bool = None, execute_if_none: bool = None): return parse_dict_item_value_or_set_by_func('__x__', dict_item_key, dict_item_key_by_arg, func_name_striped, execute_if_none)
def parse_self_d_item_value_or_set_by_func(dict_item_key: str = None, dict_item_key_by_arg: str | int = None, func_name_striped: bool = None, execute_if_none: bool = None): return parse_dict_item_value_or_set_by_func('__d__', dict_item_key, dict_item_key_by_arg, func_name_striped, execute_if_none)

def _module_name(func, module_name, module_name_striped):
    if module_name_striped:
        module_name_by_func = func.__name__.strip('_')
    else:
        module_name_by_func = func.__name__
    if module_name is None:
        return module_name_by_func
    if module_name == '#':
        return module_name_by_func
    if module_name.endswith('.#'):
        return f'{module_name[:-1]}{module_name_by_func}' # ..#
    if module_name.endswith('#'):
        return f'{module_name[:-1]}.{module_name_by_func}' # .abc#
    return module_name

def _instance(self, func, args, kwargs, module_name, arg0, module_name_striped, search_from_self, es):
    from ..functions.builtins import join_mod_path, parse_mod_path_by_pycls, instance_pyobj_by_mod_path
    from ..system.types.he import He
    ags = [self if arg0 is None else getattr(self, arg0), *args]
    module_name = _module_name(func, module_name, module_name_striped)
    if module_name.startswith('/'): # 绝对路径模块
        return instance_pyobj_by_mod_path(module_name, ags, kwargs)
    # 相对路径模块 ！需要从定义函数的类开始偏移！
    if module_name.startswith('.'):
        offset = len(module_name) - len(mod_r := module_name.lstrip('.'))
        for cls in self.__class__.__mro__:
            if issubclass(cls, He) and cls.__dict__.get(func.__name__, None):
                clsmod = parse_mod_path_by_pycls(cls)
                target_module_name = join_mod_path(*clsmod.split('.')[:-offset], mod_r)
                return instance_pyobj_by_mod_path(target_module_name, ags, kwargs)
        raise es.add(f'实例函数：[{type(self)}].[{func}]() 函数解析实例化相对模块名称 {module_name} 没有找定义函数的主类！')
    if '.' in module_name: # 直属多级子模块 ！！！只需要从定义函数的类查询多级子模块！！！
        for cls in self.__class__.__mro__:
            if issubclass(cls, He) and cls.__dict__.get(func.__name__, None):
                target_module_name = parse_mod_path_by_pycls(cls, module_name)
                return instance_pyobj_by_mod_path(target_module_name, ags, kwargs)
        raise es.add(f'多级子模块名称 {module_name} 没有找定义函数的主类！')
    # 不从 self 开始直接实例化定义函数的类的相对模块
    if search_from_self is False:
        for cls in self.__class__.__mro__:
            if issubclass(cls, He) and cls.__dict__.get(func.__name__, None):
                target_module_name = parse_mod_path_by_pycls(cls, module_name)
                try: return instance_pyobj_by_mod_path(target_module_name, ags, kwargs)
                except Exception as e: raise es.add(f'不从 self 开始直接实例化函数所在类的相对模块： {target_module_name} 失败，错误信息：{e}')
        raise es.add(f'直属子模块名称 {module_name} 没有找定义函数的主类！')
    # 从 self 开始搜索尝试实例化类的相对模块直到函数所在类
    for cls in self.__class__.__mro__:
        if issubclass(cls, He):
            target_module_name = parse_mod_path_by_pycls(cls, module_name)
            # 排查部分：-------------------------------------------------------------------------------  需要删除
            # if target_module_name == 'hebill.builtin.system.components.web_system':
            #     return instance_pyobj_by_mod_path(target_module_name, ags, kwargs)
            # ----------------------------------------------------------------------------------------------------
            try: return instance_pyobj_by_mod_path(target_module_name, ags, kwargs)
            except Exception as e:
                es.add(f'循环尝试实例化模块： {target_module_name} 未成功')
                es.add(e)
        if cls.__dict__.get(func.__name__, None): break
    raise es.add(f'直属子模块名称 {module_name} 没有找定义函数的主类！')

def instance_he_by_module_name(module_name: str = None, arg0: str = None, module_name_striped: bool = None, search_from_self: bool = None):
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            es = HeEro(self, func, f'实例化模块赋值并返回', 'instance_he_by_module_name', {'module_name': module_name, 'arg0': arg0, 'module_name_striped': module_name_striped, 'search_from_self': search_from_self})
            return _instance(self, func, args, kwargs, module_name, arg0, module_name_striped, search_from_self, es)
        return wrapper
    return decorator

def parse_dict_item_value_or_set_by_instance_he_by_module_name(dict_attr_name: str = None, dict_item_key: str = None, dict_item_key_by_arg: str | int = None, dict_item_key_by_func: bool = None, func_name_striped: bool = None, execute_if_none: bool = None, module_name: str = None, arg0: str = None, module_name_striped: bool = None, search_from_self: bool = None):
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            es = HeEro(self, func, f'获取字典值，如果没有则运行函数赋值并返回', 'parse_dict_item_value_or_set_by_instance_he_by_module_name', {'dict_attr_name': dict_attr_name, 'dict_item_key': dict_item_key, 'dict_item_key_by_arg': dict_item_key_by_arg, 'func_name_striped': execute_if_none, 'execute_if_none': module_name, 'module_name': func_name_striped, 'arg0': arg0, 'module_name_striped': module_name_striped, 'search_from_self': search_from_self})
            d, k = _dict(self, dict_attr_name, es), _key(self, func, args, kwargs, dict_item_key, dict_item_key_by_arg, dict_item_key_by_func, func_name_striped, es)
            if k not in d or (d[k] is None and execute_if_none): d[k] = _instance(self, func, args, kwargs, module_name, arg0, module_name_striped, search_from_self, es)
            return d[k]
        return wrapper
    return decorator
def parse_self_item_value_or_set_by_instance_he_by_module_name(dict_item_key: str = None, dict_item_key_by_arg: str | int = None, dict_item_key_by_func: bool = None, func_name_striped: bool = None, execute_if_none: bool = None, module_name: str = None, arg0: str = None, module_name_striped: bool = None, search_from_self: bool = None):
    return parse_dict_item_value_or_set_by_instance_he_by_module_name(None, dict_item_key, dict_item_key_by_arg, dict_item_key_by_func, func_name_striped, execute_if_none, module_name, arg0, module_name_striped, search_from_self)
def parse_self_x_item_value_or_set_by_instance_he_by_module_name(dict_item_key: str = None, dict_item_key_by_arg: str | int = None, dict_item_key_by_func: bool = None, func_name_striped: bool = None, execute_if_none: bool = None, module_name: str = None, arg0: str = None, module_name_striped: bool = None, search_from_self: bool = None):
    return parse_dict_item_value_or_set_by_instance_he_by_module_name('__x__', dict_item_key, dict_item_key_by_arg, dict_item_key_by_func, func_name_striped, execute_if_none, module_name, arg0, module_name_striped, search_from_self)
def parse_self_d_item_value_or_set_by_instance_he_by_module_name(dict_item_key: str = None, dict_item_key_by_arg: str | int = None, dict_item_key_by_func: bool = None, func_name_striped: bool = None, execute_if_none: bool = None, module_name: str = None, arg0: str = None, module_name_striped: bool = None, search_from_self: bool = None):
    return parse_dict_item_value_or_set_by_instance_he_by_module_name('__d__', dict_item_key, dict_item_key_by_arg, dict_item_key_by_func, func_name_striped, execute_if_none, module_name, arg0, module_name_striped, search_from_self)

def _set_dict_item_value_by_setter_with_agr(self, func, args, kwargs, dict_attr_name, dict_item_key, dict_item_key_by_arg, func_name_striped, value_agr_sn, value_type, es):
    d, k, val, = _dict(self, dict_attr_name, es), _key(self, func, args, kwargs, dict_item_key, dict_item_key_by_arg, False, func_name_striped, es), args[value_agr_sn or 0]
    if isinstance(value_type, str): vts = [value_type.lower()]
    elif isinstance(value_type, (list, tuple)): vts = [i.lower() for i in value_type]
    else: vts = []
    if not vts: d[k] = val; return
    def _float(v):
        if isinstance(v, (int, float)): return float(v)
        if isinstance(v, str):
            try: return float(v.replace(',', '').replace(' ', ''))
            except ValueError: return None
        return None
    def _is_scalar(v):
        return isinstance(v, (str, int, float))
    def _to_int(v, *, cond=lambda x: True):
        fv = _float(v)
        if fv is None or fv != int(fv) or not cond(fv): return None
        return int(fv)
    converters = {
        # 基础
        'bol': lambda v: bool(v),
        'bool': lambda v: bool(v),
        'non': lambda v: None,
        'none': lambda v: None,

        # 字符串
        'str': lambda v: str(v) if _is_scalar(v) else None,
        'string': lambda v: str(v) if _is_scalar(v) else None,
        'strue': lambda v: str(v) if _is_scalar(v) and str(v) else None,
        'string_unempty': lambda v: str(v) if _is_scalar(v) and str(v) else None,

        # 字典
        'dit': lambda v: dict(v) if isinstance(v, dict) else None,
        'dict': lambda v: dict(v) if isinstance(v, dict) else None,
        # 列表
        'lst': lambda v: list(v) if isinstance(v, list) else None,
        'list': lambda v: list(v) if isinstance(v, list) else None,

        # 浮点
        'flt': _float,
        'float': _float,
        'fltp': lambda v: f if (f := _float(v)) is not None and f > 0 else None,
        'float_positive': lambda v: f if (f := _float(v)) is not None and f > 0 else None,
        'fltn': lambda v: f if (f := _float(v)) is not None and f < 0 else None,
        'float_negtive': lambda v: f if (f := _float(v)) is not None and f < 0 else None,
        'fltup': lambda v: f if (f := _float(v)) is not None and f <= 0 else None,
        'float_unpositive': lambda v: f if (f := _float(v)) is not None and f <= 0 else None,
        'fltun': lambda v: f if (f := _float(v)) is not None and f >= 0 else None,
        'float_unnegtive': lambda v: f if (f := _float(v)) is not None and f >= 0 else None,
        # 整数
        'int': lambda v: _to_int(v),
        'integer': lambda v: _to_int(v),
        'intp': lambda v: _to_int(v, cond=lambda x: x > 0),
        'integer_positive': lambda v: _to_int(v, cond=lambda x: x > 0),
        'intn': lambda v: _to_int(v, cond=lambda x: x < 0),
        'integer_negtive': lambda v: _to_int(v, cond=lambda x: x < 0),
        'intup': lambda v: _to_int(v, cond=lambda x: x <= 0),
        'integer_unpositive': lambda v: _to_int(v, cond=lambda x: x <= 0),
        'intun': lambda v: _to_int(v, cond=lambda x: x >= 0),
        'integer_unnegtive': lambda v: _to_int(v, cond=lambda x: x >= 0),
        # 语言
        'lan': lambda v: v if v in self.__si__.LANS else None,
        'language': lambda v: v if v in self.__si__.LANS else None,
        # 网站请求模式
        'webappmode': lambda v: v if v in self.__si__.WEBMODS else None,
    }
    for vt in vts:
        conv = converters.get(vt)
        if not conv: raise es.add(f'不支持提供的赋值类型{vts}')
        result = conv(val)
        if result is not None:
            d[k] = result
            return
    return

def set_dict_item_value_by_setter_with_agr(dict_attr_name: str = None, dict_item_key: str = None, dict_item_key_by_arg: str | int = None, func_name_striped: bool = None, value_agr_sn:int=None, value_type:str=None):
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            es = HeEro(self, func, f'设置字典值，从 args 中获取对应值赋值', 'set_dict_item_value_by_setter_with_agr', {'dict_attr_name': dict_attr_name, 'dict_item_key': dict_item_key, 'dict_item_key_by_arg': dict_item_key_by_arg, 'func_name_striped': func_name_striped, 'value_agr_sn': value_agr_sn, 'value_type': value_type})
            _set_dict_item_value_by_setter_with_agr(self, func, args, kwargs, dict_attr_name, dict_item_key, dict_item_key_by_arg, func_name_striped, value_agr_sn, value_type, es)
            return None
        return wrapper
    return decorator
def set_self_item_value_by_setter_with_agr(dict_item_key: str = None, dict_item_key_by_arg: str | int = None, func_name_striped: bool = None, value_agr_sn:int=None, value_type:str=None): return set_dict_item_value_by_setter_with_agr(None, dict_item_key, dict_item_key_by_arg, func_name_striped, value_agr_sn, value_type)
def set_self_x_item_value_by_setter_with_agr(dict_item_key: str = None, dict_item_key_by_arg: str | int = None, func_name_striped: bool = None, value_agr_sn:int=None, value_type:str=None): return set_dict_item_value_by_setter_with_agr('__x__', dict_item_key, dict_item_key_by_arg, func_name_striped, value_agr_sn, value_type)
def set_self_d_item_value_by_setter_with_agr(dict_item_key: str = None, dict_item_key_by_arg: str | int = None, func_name_striped: bool = None, value_agr_sn:int=None, value_type:str=None): return set_dict_item_value_by_setter_with_agr('__d__', dict_item_key, dict_item_key_by_arg, func_name_striped, value_agr_sn, value_type)

def _redirect_to_attribute_function(self, func, args, kwargs, func_attr_name, func_name_striped, es):
    ns = func_attr_name.split('.')
    if ns[-1].endswith('#'):
        ns[-1] = ns[-1].strip('#')
        ns.append(func.__name__.strip('_') if func_name_striped else func.__name__)
    def loop(o, i):
        if not hasattr(o, ns[i]):
            raise es.add(f'self.{'.'.join(ns[:i])} 函数属性不存在！')
        r = getattr(o, ns[i])
        if i == len(ns) - 1: return r
        return loop(r, i + 1)
    f = loop(self, 0)
    if callable(f):
        try: return f(*args, **kwargs)
        except Exception as e: return es.add(f'self.{'.'.join(ns)} 属性函数运行失败: {e}！')
    raise es.add(f'self.{'.'.join(ns)} 属性不不是函数！')
def redirect_to_attribute_function(func_attr_name: str, func_name_striped: bool = None):
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            es = HeEro(self, func, f'函数转发', 'redirect_to_attribute_function', {'func_attr_name': func_attr_name, 'func_name_striped': func_name_striped})
            return _redirect_to_attribute_function(self, func, args, kwargs, func_attr_name, func_name_striped, es)
        return wrapper
    return decorator

def _redirect_to_attribute_property(self, func, func_attr_name, func_name_striped, es):
    ns = func_attr_name.split('.')
    if ns[-1].endswith('#'):
        ns[-1] = ns[-1].strip('#')
        ns.append(func.__name__.strip('_') if func_name_striped else func.__name__)
    def loop(o, i):
        if not hasattr(o, ns[i]):
            raise es.add(f'self.{'.'.join(ns[:i])} 属性不存在！')
        r = getattr(o, ns[i])
        if i == len(ns) - 1: return r
        return loop(r, i + 1)
    return loop(self, 0)
def redirect_to_attribute_property(func_attr_name: str, func_name_striped: bool = None):
    def decorator(func):
        def wrapper(self):
            es = HeEro(self, func, f'属性转发', 'redirect_to_attribute_property', {'func_attr_name': func_attr_name, 'func_name_striped': func_name_striped})
            return _redirect_to_attribute_property(self, func, func_attr_name, func_name_striped, es)
        return wrapper
    return decorator
