from ..he import He
from .number import Number


class Hf(He, float, Number):
    def __new__(cls, u, number: str | float | int):
        if isinstance(number, str):
            try: number = float(number.replace(',', '').replace(' ', ''))
            except: raise RuntimeError('实例化 Hn 实例参数 number 必须支持 float(number)。')
        if not isinstance(number, float | int):
            raise RuntimeError('实例化 Hn 实例参数 number 只支持 str | float | int 。')
        # noinspection PyTypeChecker
        obj = float.__new__(cls, number)
        obj.u = u
        return obj

    def __init__(self, u, number: str | float | int):
        He.__init__(self, u)

