from .....multilinguals import Multilinguals as ModMultilinguals


class Multilinguals(ModMultilinguals):
    def __init__(self, u):
        super().__init__(u, folder=u.data_multilinguals_folder)
    # @@@@@@@@@！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！
    # 由于 webmod 在类中缓存了，所以一单在 __init__ 中绑定页面刷新就不会重新实例化，但是系统一直运行，这里重写函数
    @property
    def ___hooked_configs___(self): return self.__u__.website.client.request.address
