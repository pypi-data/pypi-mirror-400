from datetime import datetime, tzinfo

from ....functions.decorators import parse_dict_item_value_or_set_by_func
from .....builtin.functions.decorators import parse_self_x_item_value_or_set_by_func


class Number:
    CN_INTEGER_0_TO_9 = '零壹贰叁肆伍陆柒捌玖'
    CN_POINTS_UNITS = '角分厘毫丝'
    CN_DECIMAL_4S_UNITS = '万亿兆京垓秭穰沟涧正载极'
    CN_DECIMAL_UNITS = '拾佰仟'

    CN_CURRENCY_UNIT = "圆"
    CN_POINT_NAME = '点'
    CN_ONLY_NAME = '整'
    CN_CNY_NAME = '人民币'
    CN_USD_NAME = '美元'
    CN_EUR_NAME = '欧元'
    CN_MINUS = '负'

    EN_CNY_NAME = 'Say Chinese Yuan'
    EN_USD_NAME = 'Say U.S.Dollar'
    EN_EUR_NAME = 'Say Euro'
    EN_ONLY_NAME = 'Only'
    EN_POINT_NAME = 'Point'
    EN_AND_NAME = 'and'
    EN_MINUS = 'Minus'

    EN_INTEGER_0_TO_9 = ['Zero', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine']
    EN_INTEGER_1NS = ['Ten', 'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen', 'Seventeen',
                      'Eighteen', 'Nineteen']
    EN_INTEGER_2NS = ['Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety']
    EN_HUNDRED_NAME = 'Hundred'
    EN_DECIMAL_3S_UNITS = ['Thousand', 'Million', 'Billion', 'Trillion', 'Quadrillion', 'Quintillion', 'Sextillion',
                           'Septillion', 'Octillion', 'Nonillion', 'Decillion']
    EN_POINTS_UNITS = ['Dime', 'Cent', 'Mill']

    WEIGHT_UNIT_KGS = 'Kgs'
    CN_WEIGHT_UNIT_KGS = '公斤'
    EN_WEIGHT_UNIT_KGS = 'Kilograms'

    LENGTH_UNIT_MM = 'mm'
    CN_LENGTH_UNIT_MM = '毫米'
    EN_LENGTH_UNIT_MM = 'Millimetres'

    LENGTH_UNIT_M = 'm'
    CN_LENGTH_UNIT_M = '米'
    EN_LENGTH_UNIT_M = 'Metres'

    LENGTH_UNIT_CM = 'cm'
    CN_LENGTH_UNIT_CM = '厘米'
    EN_LENGTH_UNIT_CM = 'Centimeters'

    def is_int(self): return int(self) == self
    def is_positive(self): return self > 0
    def is_negative(self): return self < 0
    def is_zero(self): return self == 0

    def round(self, digits: int = 0):
        r = self.__round__(digits)
        if digits > 0: return self.__st__.hf(r)
        return self.__st__.hi(r)
    def ceil(self, digits: int = 0):
        r = (self / 10**(-digits)).__ceil__() * 10 **(-digits)
        if digits > 0: return self.__st__.hf(r)
        return self.__st__.hi(r)
    def floor(self, digits: int = 0):
        r = (self / 10**(-digits)).__floor__() * 10 **(-digits)
        if digits > 0: return self.__st__.hf(r)
        return self.__st__.hi(r)

    @property
    @parse_self_x_item_value_or_set_by_func()
    def integer_part(self):
        return str(abs(int(self)))
    @property
    @parse_self_x_item_value_or_set_by_func()
    def ___integer_part_breaks___(self): return {}
    @parse_dict_item_value_or_set_by_func(dict_attr_name='___integer_part_breaks___', dict_item_key_by_arg=0)
    def integer_part_breaks(self, step: int): return [self.integer_part[max(i - step, 0):i] for i in range(len(self.integer_part), 0, -step)][::-1]
    @property
    @parse_self_x_item_value_or_set_by_func()
    def ___integer_part_strict_breaks___(self): return {}
    @parse_dict_item_value_or_set_by_func(dict_attr_name='___integer_part_strict_breaks___', dict_item_key_by_arg=0)
    def integer_part_strict_breaks(self, step: int): return [self.integer_part_breaks(step)[0].zfill(step), *self.integer_part_breaks(step)[1:]]

    @property
    @parse_self_x_item_value_or_set_by_func()
    def integer_part_myriad_breaks(self): return self.integer_part_breaks(4)
    @property
    @parse_self_x_item_value_or_set_by_func()
    def integer_part_myriad_strict_breaks(self): return self.integer_part_strict_breaks(4)
    @property
    @parse_self_x_item_value_or_set_by_func()
    def integer_part_thousand_breaks(self): return self.integer_part_breaks(3)
    @property
    @parse_self_x_item_value_or_set_by_func()
    def integer_part_thousand_strict_breaks(self): return self.integer_part_strict_breaks(3)

    @property
    @parse_self_x_item_value_or_set_by_func()
    def decimal_part(self): return '' if '.' not in (s:=str(self)) or (r:=s.split('.', 1)[1]) == '0' else r
    ####################################################################################################
    def round_format(self, digits: int = 0, force_digits: bool = None, integer_breaks: int = 3): return f'{','.join((n:=self.round(digits)).integer_part_breaks(integer_breaks))}{'.' + r if (r:=n.decimal_part.ljust(digits, '0') if digits > 0 and force_digits else n.decimal_part) else ''}'

    def year(self, tz: tzinfo = None): return datetime.fromtimestamp(self, tz).year
    def month(self, tz: tzinfo = None): return datetime.fromtimestamp(self, tz).month
    def day(self, tz: tzinfo = None): return datetime.fromtimestamp(self, tz).day
    def hour(self, tz: tzinfo = None): return datetime.fromtimestamp(self, tz).hour
    def minute(self, tz: tzinfo = None): return datetime.fromtimestamp(self, tz).minute
    def second(self, tz: tzinfo = None): return datetime.fromtimestamp(self, tz).second

    def format_yy(self, tz: tzinfo = None): return str(self.year(tz))[-2:]
    def format_m(self, tz: tzinfo = None): return str(self.month(tz))
    def format_d(self, tz: tzinfo = None): return str(self.day(tz))
    def format_h(self, tz: tzinfo = None): return str(self.hour(tz))
    def format_i(self, tz: tzinfo = None): return str(self.minute(tz))
    def format_s(self, tz: tzinfo = None): return str(self.second(tz))
    def format_yyyy(self, tz: tzinfo = None): return str(self.year(tz))
    def format_mm(self, tz: tzinfo = None): return str(self.month(tz)).rjust(2, '0')
    def format_dd(self, tz: tzinfo = None): return str(self.day(tz)).rjust(2, '0')
    def format_hh(self, tz: tzinfo = None): return str(self.hour(tz)).rjust(2, '0')
    def format_ii(self, tz: tzinfo = None): return str(self.minute(tz)).rjust(2, '0')
    def format_ss(self, tz: tzinfo = None): return str(self.second(tz)).rjust(2, '0')

    def format_yymd(self, tz: tzinfo = None, delimiter='-'): return f'{self.format_yy(tz)}{(d:=delimiter)}{self.format_m(tz)}{d}{self.format_d(tz)}'
    def format_his(self, tz: tzinfo = None, delimiter=':'): return f'{self.format_h(tz)}{(d:=delimiter)}{self.format_i(tz)}{d}{self.format_s(tz)}'
    def format_yymdhis(self, tz: tzinfo = None, delimiter=' ', date_delimiter='-', time_delimiter=':'): return f'{self.format_yymd(tz, date_delimiter)}{delimiter}{self.format_his(tz, time_delimiter)}'
    def format_yyyymmdd(self, tz: tzinfo = None, delimiter='-'): return f'{self.format_yyyy(tz)}{(dd:=delimiter)}{self.format_mm(tz)}{dd}{self.format_dd(tz)}'
    def format_hhiiss(self, tz: tzinfo = None, delimiter=':'): return f'{self.format_hh(tz)}{(td:=delimiter)}{self.format_ii(tz)}{td}{self.format_ss(tz)}'
    def format_yyyymmddhhiiss(self, tz: tzinfo = None, delimiter=' ', date_delimiter='-', time_delimiter=':'): return f'{self.format_yyyymmdd(tz, date_delimiter)}{delimiter}{self.format_hhiiss(tz, time_delimiter)}'

    ####################################################################################################
    # 以下数字转化为大写
    ####################################################################################################

    @property
    @parse_self_x_item_value_or_set_by_func()
    def cn_decimal_part(self):
        if not self.decimal_part: return ''
        cn = ''
        for i in range(0, len(self.decimal_part)):
            cn += self.CN_INTEGER_0_TO_9[int(self.decimal_part[i])]
        return cn

    def _capitalized_myriad_breaks_number_to_cn(self, group_sn, num_sn):
        num = int(self.integer_part_myriad_strict_breaks[group_sn][num_sn])
        cap = f'{self.CN_INTEGER_0_TO_9[int(self.integer_part_myriad_strict_breaks[group_sn][num_sn])]}'
        if num != 0 and num_sn < 3:
            cap += f'{self.CN_DECIMAL_UNITS[2 - num_sn]}'
        return cap

    @property
    @parse_self_x_item_value_or_set_by_func()
    def cn_integer_part(self):
        bs, qnt, cn, first, zero = self.integer_part_myriad_strict_breaks, len(self.integer_part_myriad_strict_breaks), '', True, False
        for i, block in enumerate(bs):
            part = ''
            for j, c in enumerate(block):
                if c != '0':
                    if zero and not first: part += self.CN_INTEGER_0_TO_9[0]
                    part += self.CN_INTEGER_0_TO_9[int(c)]
                    if j < 3: part += self.CN_DECIMAL_UNITS[2 - j]
                    first = zero = False
                else: zero = True
            cn += part
            if part and i < qnt - 1: cn += self.CN_DECIMAL_4S_UNITS[qnt - i - 2]
        if self.is_negative(): return f'{self.CN_MINUS}{cn or self.CN_INTEGER_0_TO_9[0]}'
        return cn or self.CN_INTEGER_0_TO_9[0]

    @property
    @parse_self_x_item_value_or_set_by_func()
    def cn_number(self): return f'{self.cn_integer_part}{self.CN_POINT_NAME}{self.cn_decimal_part}' if self.cn_decimal_part else self.cn_integer_part
    @property
    @parse_self_x_item_value_or_set_by_func()
    def cn_money(self):
        cn, dp = self.cn_integer_part + self.CN_CURRENCY_UNIT, self.decimal_part
        if not dp: return cn + self.CN_ONLY_NAME
        units, nums, tail = self.CN_POINTS_UNITS, self.CN_INTEGER_0_TO_9, ''
        for i in range(min(5, len(dp)) - 1, -1, -1):
            if dp[i] != '0' or tail: tail = nums[int(dp[i])] + units[i] + tail
        return cn + (tail or self.CN_ONLY_NAME)
    @property
    @parse_self_x_item_value_or_set_by_func()
    def cn_cny(self): return self.CN_CNY_NAME + self.cn_money
    def cn_usd(self): return self.CN_USD_NAME + self.cn_money
    def cn_eur(self): return self.CN_EUR_NAME + self.cn_money
    # noinspection PyTypeHints
    @property
    @parse_self_x_item_value_or_set_by_func()
    def en_decimal_part(self): return ' '.join(self.EN_INTEGER_0_TO_9[int(n)] for n in self.decimal_part)
    def _capitalized_en_by_thousands_breaks_add_and(self, group_sn, number_sn):
        for i in range(number_sn + 1, 3):
            if self.integer_part_thousand_strict_breaks[group_sn][i] != '0': return True
        return False
    # noinspection PyTypeHints
    def _capitalized_en_by_thousands_breaks(self, group_sn):
        g = self.integer_part_thousand_strict_breaks[group_sn]
        caps = []
        if g[0] != '0':
            caps.append(self.EN_INTEGER_0_TO_9[int(g[0])])
            caps.append(self.EN_HUNDRED_NAME)
            if self._capitalized_en_by_thousands_breaks_add_and(group_sn, 0): caps.append(self.EN_AND_NAME)
            caps.extend(self._capitalized_en_by_thousands_breaks_2(group_sn))
        else: caps.extend(self._capitalized_en_by_thousands_breaks_2(group_sn))
        return caps
    # noinspection PyTypeHints
    def _capitalized_en_by_thousands_breaks_2(self, group_sn):
        g = self.integer_part_thousand_strict_breaks[group_sn]
        caps = []
        if int(g[1]) >= 2:
            caps.append(self.EN_INTEGER_2NS[int(g[1]) - 2])
            caps.extend(self._capitalized_en_by_thousands_breaks_1(group_sn))
        elif g[1] == '1': caps.append(self.EN_INTEGER_1NS[int(g[2])])
        else: caps.extend(self._capitalized_en_by_thousands_breaks_1(group_sn))
        return caps
    # noinspection PyTypeHints sd
    def _capitalized_en_by_thousands_breaks_1(self, group_sn):
        g = self.integer_part_thousand_strict_breaks[group_sn]
        caps = []
        if g[2] != '0': caps.append(self.EN_INTEGER_0_TO_9[int(g[2])])
        return caps
    # noinspection PyTypeHints
    @property
    @parse_self_x_item_value_or_set_by_func()
    def en_integer_part(self):
        bs, caps, q = self.integer_part_thousand_strict_breaks, [], len(self.integer_part_thousand_strict_breaks)
        for i, g in enumerate(bs):
            group_caps = self._capitalized_en_by_thousands_breaks(i)
            if not group_caps: continue  # 全 0 group 跳过，不加 unit
            caps.extend(group_caps)
            # 只在当前 group 有数字时加 unit
            if i < q - 1 and any(x != '0' for x in bs[i]): caps.append(self.EN_DECIMAL_3S_UNITS[q - i - 2])
        en = ' '.join(caps) or self.EN_INTEGER_0_TO_9[0]
        return f'{self.EN_MINUS} {en}' if self.is_negative() else en
    @property
    @parse_self_x_item_value_or_set_by_func()
    def en_number(self): return f'{self.en_integer_part} {self.EN_POINT_NAME} {self.en_decimal_part}' if self.en_decimal_part else self.en_integer_part
    @property
    @parse_self_x_item_value_or_set_by_func()
    def en_money(self):
        en = self.en_integer_part
        ds = []
        # 遍历小数部分，每位对应 EN_POINTS_UNITS
        for i, digit in enumerate(self.decimal_part[:3]):  # 只处理前三位
            n = int(digit)
            if n == 0 and not ds: continue  # 前导零且还没有加入其他小数
            # noinspection PyTypeHints
            unit = self.EN_POINTS_UNITS[i]
            if n > 1: unit += 's'
            ds.append(unit)
            # noinspection PyTypeHints
            ds.append(self.EN_INTEGER_0_TO_9[n])
        if ds:
            ds.reverse()  # 小数位从高到低
            en += f' {self.EN_AND_NAME} ' + ' '.join(ds)
        else: en += f' {self.EN_ONLY_NAME}'
        return en

    @property
    @parse_self_x_item_value_or_set_by_func()
    def en_cny(self): return self.EN_CNY_NAME + ' ' + self.en_money
    @property
    @parse_self_x_item_value_or_set_by_func()
    def en_usd(self): return self.EN_USD_NAME + ' ' + self.en_money
    @property
    @parse_self_x_item_value_or_set_by_func()
    def en_eur(self): return self.EN_EUR_NAME + ' ' + self.en_money
