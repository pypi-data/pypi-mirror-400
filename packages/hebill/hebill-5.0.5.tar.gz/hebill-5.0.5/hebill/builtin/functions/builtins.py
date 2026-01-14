import inspect
import os
import subprocess
import sys
from types import ModuleType


class HeEro(Exception):
    def __init__(self, he=None, func=None, feature=None, dec=None, dec_kwargs=None, error=None):
        super().__init__(None)
        self.es = []
        self.he = None if he is None else he if isinstance(he, type) else type(he)
        self.func = func if isinstance(func, str) else None if func is None else func.__name__
        self.feature = feature
        self.dec = dec
        self.dec_kwargs = dec_kwargs or {}
        self.add(error)

    def add(self, *e):
        if e is None:
            return self
        for i in e: self.es.append(i)
        return self

    def output(self):
        def loop(e, level=0):
            pad = '  | ' * level
            lines = [
                f'{pad}####################################################################################################',
                f'{pad}*** {e.feature or "[功能说明未提供]"} ***',
            ]
            if e.he:
                lines.append(f'{pad}{e.he.__module__}.{e.he.__name__}:')
            if e.dec:
                args = ', '.join(f'{k}={v!r}' for k, v in e.dec_kwargs.items())
                lines.append(f'{pad}@{e.dec}({args})')
            if e.func:
                lines.append(f'{pad}def {e.func}(self, *args, **kwargs): ...')
            # lines.append(f'{pad}--------------------------------------------------------------------------------------------------')
            for i in e.es:
                if isinstance(i, HeEro):
                    lines.append(f'{pad}  > 子错误：')
                    lines.extend(loop(i, level + 1))
                else:
                    lines.append(f'{pad}  > {i}')
            return lines
        return '\n' + '\n'.join(loop(self))

    def __str__(self):
        return self.output()

def parse_attribute_by_path_name(pyobj: object, path_name: str):
    from operator import attrgetter
    return attrgetter(path_name)(pyobj)

def join_url(*names):
    ns = [n for i in names if (n := (i or '').strip('/'))]
    if len(ns) == 0: return ''
    if len(ns) == 1: return ns[0]
    if names[0] == '/' or names[0] == '//': return names[0] + '/'.join(['', *ns])
    return '/'.join(ns)

def join_mod_path(*names):
    return '.'.join(i for n in names if (i := (n or '').strip('.')))

def parse_pycls_name_by_mod_path(module_path: str):
    return ''.join(w.capitalize() for w in module_path.split('.')[-1].split('_'))

def parse_mod_path_by_rel_path(mod_path: str, rel_path: str):
        if not rel_path: return mod_path
        if not rel_path.startswith('.'): return join_mod_path('.'.join([mod_path, rel_path]))
        mod_path_right = rel_path.lstrip('.')
        mod_path_offset = len(rel_path) - len(mod_path_right)
        ns = mod_path.split('.')
        if len(ns) <= mod_path_offset: raise RuntimeError('"."的数量超出范围')
        return join_mod_path('.'.join([*ns[:-mod_path_offset], mod_path_right]) if mod_path_right else '.'.join(ns[:-mod_path_offset]))


def parse_mod_path_by_pycls(pycls: type, *sub_names):
    return join_mod_path(*pycls.__module__.split('.')[:-1], *sub_names)

def parse_mod_path_by_pyobj(pyobj: object, *sub_names):
    return parse_mod_path_by_pycls(pyobj.__class__, *sub_names)

def parse_dirpath_by_pymod(pymod: ModuleType):
    return os.path.dirname(pymod.__file__)

def parse_dirpath_by_pycls(pycls: type):
    return os.path.dirname(inspect.getfile(pycls))

def parse_dirpath_by_pyobj(pyobj: object):
    return parse_dirpath_by_pycls(pyobj.__class__)

def import_pymod_by_mod_path(module_path: str):
    return __import__(module_path, fromlist=[''])

def import_pycls_by_mod_path(module_path: str):
    return getattr(import_pymod_by_mod_path(f'{module_path}.core'), parse_pycls_name_by_mod_path(module_path))

def instance_pyobj_by_pycls(pycls: type, args=None, kwargs=None):
    return pycls(*(args if args else []), **(kwargs if kwargs else {}))

def instance_pyobj_by_mod_path(module_path: str, args=None, kwargs=None):
    return instance_pyobj_by_pycls(import_pycls_by_mod_path(module_path), args, kwargs)

def import_webapp_pycls_by_mod_path(module_path: str):
    return getattr(import_pymod_by_mod_path(f'{module_path}.core'), 'Core')

def timestamp_days(): return timestamp_nanoseconds() // (24 * 60 * 60 * 1000000000)
def timestamp_hours(): return timestamp_nanoseconds() // (24 * 60 * 1000000000)
def timestamp_seconds(): return timestamp_nanoseconds() // 1000000000
def timestamp_milliseconds(): return timestamp_nanoseconds() // 1000000
def timestamp_microseconds(): return timestamp_nanoseconds() // 1000
def timestamp_nanoseconds(): import time; return time.time_ns()


BASE64URL: str = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_"
def base_convert(value: str, base_from=10, base_to=32):
    if not (2 <= base_from <= 64) or not (2 <= base_to <= 64): raise RuntimeError('进制转换支持范围： 2 - 64，参数超出范围')
    if base_from == base_to: return value
    digits = BASE64URL[:base_to]
    # 转为 10 进制整数
    num = 0
    for ch in value:
        idx = digits.find(ch)
        if idx == -1: raise ValueError(f"进制转换不支持字符：'{ch}' for base {base_from}")
        num = num * base_from + idx
    if num == 0: return digits[0]
    out = []
    while num > 0:
        num, r = divmod(num, base_to)
        out.append(digits[r])
    return ''.join(reversed(out))
def uid_generater(prefix=None):
    import secrets
    return (prefix or '') + base_convert(f"{timestamp_nanoseconds()}{secrets.randbelow(10 ** 6):06d}", 10, 64)
# COMPRESS_ID 字符必须相等长度
COMPRESS_ID_STR: str = 'ST'
COMPRESS_ID_INT: str = 'IN'
COMPRESS_ID_FLT: str = 'FT'
COMPRESS_ID_DIT: str = 'DT'
COMPRESS_ID_LST: str = 'LT'
COMPRESS_ID_BOL: str = 'BL'
COMPRESS_ID_NON: str = 'NO'
def compress(data: dict | list | int | float | bool | str | None) -> str:
    import json, zlib, base64
    if isinstance(data, dict): t, d = COMPRESS_ID_DIT, json.dumps(data, separators=(',', ':')).encode()
    elif isinstance(data, list): t, d = COMPRESS_ID_LST, json.dumps(data, separators=(',', ':')).encode()
    elif isinstance(data, str): t, d = COMPRESS_ID_STR, data.encode()
    elif isinstance(data, int): t, d = COMPRESS_ID_INT, str(data).encode()
    elif isinstance(data, float): t, d = COMPRESS_ID_FLT, str(data).encode()
    elif isinstance(data, bool): t, d = COMPRESS_ID_BOL, b'1' if data else b'0'
    elif data is None: t, d = COMPRESS_ID_NON, b''
    else: raise TypeError(f"不支持压缩类型： {type(data)}")
    return f"{t}{base64.urlsafe_b64encode(zlib.compress(d, level=9)).rstrip(b'=').decode()}"
def decompress(data: str) -> dict | list | int | float | bool | str | None:
    import json, zlib, base64
    # if not data: raise ValueError("空字符串解压失败")
    if not data: return None
    t, d = data[:(l:=len(COMPRESS_ID_STR))], data[l:]
    try: r = zlib.decompress(base64.urlsafe_b64decode(d + '=' * (-len(d) % 4))).decode()
    except: raise ValueError("字符串解压失败")
    if t == COMPRESS_ID_DIT: return json.loads(r)
    if t == COMPRESS_ID_LST: return json.loads(r)
    if t == COMPRESS_ID_STR: return r
    if t == COMPRESS_ID_INT: return int(r)
    if t == COMPRESS_ID_FLT: return float(r)
    if t == COMPRESS_ID_BOL: return r == b'1'
    if t == COMPRESS_ID_NON: return None
    return None

def var2ui(value): return str(value) if isinstance(value, str) else f'"{value}"'

def terminal(cmd: list[str] | str):
    try:
        # 如果是字符串，转换为列表，防止 shell injection
        cmd_list = cmd if isinstance(cmd, list) else cmd.split()
        # 执行命令
        print(f' > {' ' .join(cmd_list)}')
        result = subprocess.run(
            cmd_list,
            shell=False,
            # check=False,  # 我们手动处理 returncode
            # stdout=subprocess.PIPE,
            # stderr=subprocess.PIPE,
            # text=True  # 输出以 str 而不是 bytes
        )
        return result.returncode == 0
    except Exception as e:
        """print(f"[terminal error] {e}", file=sys.stderr)"""
        return False

