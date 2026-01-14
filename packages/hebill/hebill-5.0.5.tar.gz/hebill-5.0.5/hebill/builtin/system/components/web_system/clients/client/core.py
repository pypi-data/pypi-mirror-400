from ......functions.builtins import timestamp_seconds
from ......functions.decorators import parse_self_item_value, \
    parse_self_item_value_or_set_by_instance_he_by_module_name
from .....types.hd import Hd


class Client(Hd):
    def __init__(self, u, uid):
        super().__init__(u)
        self['uid'] = uid
        self['expiry'] = self.__configs__['session_expiry'] + timestamp_seconds()

    @property
    def __websystem__(self): return self.__clients__.__websystem__
    @property
    def __clients__(self): return self.__u__
    @property
    def __configs__(self): return self.__websystem__.configs

    @property
    @parse_self_item_value()
    def uid(self): return
    @property
    @parse_self_item_value()
    def expiry(self): return

    @property
    @parse_self_item_value_or_set_by_instance_he_by_module_name()
    def request(self): return

    def hook_session(self, session: dict): self['session'] = session

    @property
    @parse_self_item_value()
    def session(self): return

    @parse_self_item_value_or_set_by_instance_he_by_module_name()
    def address(self, mode=None, module=None, arguments=None, keyword=None, page=None, orders=None, filters=None, items_per_page=None, pages_per_group=None, reference=None, language=None, security=None): return
    def url(self, mode=None, module=None, arguments=None, keyword=None, page=None, orders=None, filters=None, items_per_page=None, pages_per_group=None, reference=None, language=None, security=None): return self.address(mode, module, arguments, keyword, page, orders, filters, items_per_page, pages_per_group, reference, language, security).output()
    def redirect(self, mode=None, module=None, arguments=None, keyword=None, page=None, orders=None, filters=None, items_per_page=None, pages_per_group=None, reference=None, language=None, security=None): return self.address(mode, module, arguments, keyword, page, orders, filters, items_per_page, pages_per_group, reference, language, security).redirect()
