from ..he import He
from ..hf.number import Number


class Hi(He, int, Number):
    def __new__(cls, u, number: str | float | int):
        if isinstance(number, str):
            try: number = float(number.replace(',', ''))
            except: raise RuntimeError('实例化 Hi 实例参数 number 必须支持 float(number)。')
        if not isinstance(number, float | int):
            raise RuntimeError('实例化 Hi 实例参数 number 只支持 str | float | int 。')
        if number != int(number):
            raise RuntimeError('实例化 Hi 实例参数 number 转化为数字后必须为整型 。')
        # noinspection PyTypeChecker
        obj = int.__new__(cls, int(number))
        obj.u = u
        return obj

    def __init__(self, u, number: str | float | int):
        He.__init__(self, u)
