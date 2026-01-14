from ........functions.decorators import parse_self_item_value
from .......types.hd import Hd


class Headers(Hd):
    @property
    def __websystem__(self): return self.__clients__.__websystem__
    @property
    def __clients__(self): return self.__client__.__clients__
    @property
    def __client__(self): return self.__request__.__client__
    @property
    def __request__(self): return self.__u__
    @property
    def __configs__(self): return self.__websystem__.configs

    @property
    @parse_self_item_value()
    def host(self): return
    @property
    @parse_self_item_value()
    def connection(self): return
    @property
    @parse_self_item_value()
    def cache_control(self): return
    @property
    @parse_self_item_value()
    def sec_ch_ua(self): return
    @property
    @parse_self_item_value()
    def sec_ch_ua_mobile(self): return
    @property
    @parse_self_item_value()
    def sec_ch_ua_platform(self): return
    @property
    @parse_self_item_value()
    def upgrade_insecure_requests(self): return
    @property
    @parse_self_item_value()
    def user_agent(self): return
    @property
    @parse_self_item_value()
    def accept(self): return
    @property
    @parse_self_item_value()
    def sec_fetch_site(self): return
    @property
    @parse_self_item_value()
    def sec_fetch_mode(self): return
    @property
    @parse_self_item_value()
    def sec_fetch_user(self): return
    @property
    @parse_self_item_value()
    def sec_fetch_dest(self): return
    @property
    @parse_self_item_value()
    def accept_encoding(self): return
    @property
    @parse_self_item_value()
    def accept_language(self): return
    @property
    @parse_self_item_value()
    def cookie(self): return

