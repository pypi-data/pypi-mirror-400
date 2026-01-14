from decimal import Decimal
from ..he import He
from ..hf.number import Number

class Hm(He, Number, Decimal):
    def __new__(cls, u, number: str | float | int):
        """
        __new__ 负责创建实例
        - str 类型：去掉逗号和空格，转 Decimal
        - int 类型：直接 Decimal
        - float 类型：先转 str 再转 Decimal 避免浮点误差
        """
        if isinstance(number, str):
            try: number = Decimal(number.replace(',', '').replace(' ', ''))
            except Exception: raise RuntimeError('实例化 Hm 实例参数 number 必须支持 Decimal(number)。')
        elif isinstance(number, int):
            number = Decimal(number)
        elif isinstance(number, float):
            number = Decimal(str(number))
        else:
            raise RuntimeError('实例化 Hm 实例参数 number 只支持 str | float | int 。')
        # 使用 Decimal.__new__ 创建实例
        obj = Decimal.__new__(cls, number)
        obj.u = u
        return obj

    def __init__(self, u, number: str | float | int):
        """
        __init__ 初始化 He 部分
        """
        He.__init__(self, u)
