from .......functions.builtins import compress, join_url
from .......functions.decorators import parse_self_item_value_or_set_by_func, set_self_item_value_by_setter_with_agr, parse_self_item_value
from .....configs import Configs


class Address(Configs):
    def __init__(self, client, mode: str = None, module: str = None, arguments: dict[str,str] = None, keyword: str = None, page: int = None, orders: dict[str,str] = None, filters: dict[str,str] = None, items_per_page: int = None, pages_per_group: int = None, reference: str = None, language: str = None, security: str = None):
        Configs.__init__(self, client)
        self.mode = mode
        self.module = module
        self.arguments = arguments
        self.keyword = keyword
        self.page = page
        self.orders = orders
        self.filters = filters
        self.items_per_page = items_per_page
        self.pages_per_group = pages_per_group
        self.reference = reference
        self.language = language
        self.security = security
        self.___defaults___.update(self)

    @property
    def __client__(self): return self.__u__
    @property
    def ___websystem_configs___(self): return self.__client__.__websystem__.configs

    @property
    @parse_self_item_value_or_set_by_func(execute_if_none=True)
    def language(self): return self.__client__.request.address.language
    @language.setter
    @set_self_item_value_by_setter_with_agr(value_type='language')
    def language(self, value): pass
    def is_language_chinese(self): return self.language == 'cn'
    def is_language_english(self): return self.language == 'gb'
    def set_language_chinese(self): self.language = 'cn'
    def set_language_english(self): self.language = 'gb'

    @property
    @parse_self_item_value_or_set_by_func(execute_if_none=True)
    def mode(self): return 'page'
    @mode.setter
    @set_self_item_value_by_setter_with_agr(value_type='webappmode')
    def mode(self, value): pass
    def is_mode_page(self): return self.mode == 'page'
    def is_mode_json(self): return self.mode == 'json'
    def is_mode_ajax(self): return self.mode == 'ajax'
    def is_mode_grid(self): return self.mode == 'grid'
    def is_mode_file(self): return self.mode == 'file'
    def is_mode_not_page(self): return not self.is_mode_page()
    def is_mode_not_json(self): return not self.is_mode_json()
    def is_mode_not_ajax(self): return not self.is_mode_ajax()
    def is_mode_not_grid(self): return not self.is_mode_grid()
    def is_mode_not_file(self): return not self.is_mode_file()

    @property
    @parse_self_item_value_or_set_by_func(execute_if_none=True)
    def module(self): return ''
    @module.setter
    @set_self_item_value_by_setter_with_agr(value_type='str')
    def module(self, value): pass

    @property
    @parse_self_item_value_or_set_by_func(execute_if_none=True)
    def security(self): return ''
    @security.setter
    @set_self_item_value_by_setter_with_agr(value_type='str')
    def security(self, value): pass

    @property
    @parse_self_item_value_or_set_by_func(execute_if_none=True)
    def arguments(self): return {}
    @arguments.setter
    @set_self_item_value_by_setter_with_agr(value_type='dit')
    def arguments(self, value): pass

    @property
    @parse_self_item_value()
    def keyword(self): return
    @keyword.setter
    @set_self_item_value_by_setter_with_agr(value_type=('str', 'non'))
    def keyword(self, value):pass

    @property
    @parse_self_item_value_or_set_by_func(execute_if_none=True)
    def page(self): return 1
    @page.setter
    @set_self_item_value_by_setter_with_agr(value_type='intp')
    def page(self, value): pass

    @property
    @parse_self_item_value_or_set_by_func(execute_if_none=True)
    def orders(self): return {}
    @orders.setter
    @set_self_item_value_by_setter_with_agr(value_type='dit')
    def orders(self, value): pass

    @property
    @parse_self_item_value_or_set_by_func(execute_if_none=True)
    def filters(self): return {}
    @filters.setter
    @set_self_item_value_by_setter_with_agr(value_type='dit')
    def filters(self, value): pass

    @property
    @parse_self_item_value_or_set_by_func(execute_if_none=True)
    def items_per_page(self): return self.___websystem_configs___.pagination_items_per_page
    @items_per_page.setter
    @set_self_item_value_by_setter_with_agr(value_type='intp')
    def items_per_page(self, value): pass

    @property
    @parse_self_item_value_or_set_by_func(execute_if_none=True)
    def pages_per_group(self): return self.___websystem_configs___.pagination_pages_per_group
    @pages_per_group.setter
    @set_self_item_value_by_setter_with_agr(value_type='intp')
    def pages_per_group(self, value):  pass

    @property
    @parse_self_item_value_or_set_by_func(execute_if_none=True)
    def reference(self): return ''
    @reference.setter
    @set_self_item_value_by_setter_with_agr(value_type='str')
    def reference(self, value: str): pass

    def copy(self):
        address = Address(self.__client__)
        address.update(self.data())
        return address

    def output(self):
        cs = self.___websystem_configs___
        data = self.data()
        url = [self.___websystem_configs___.url_root_path.strip('/'), data[cs.url_key_mode]]
        data.__delitem__(cs.url_key_mode)
        url.append(compress(self.data()))
        return join_url(*url)
        if self.___websystem_configs___.url_root_path.strip('/'):
            return f'/{self.___websystem_configs___.url_root_path.strip('/')}/{url}'
        return f'/{url}'
    def update(self, m: dict, /, **kwargs):
        for k, v in m.items():
            match k:
                case 'mode' | self.___websystem_configs___.url_key_mode: self.mode = v
                case 'module' | self.___websystem_configs___.url_key_module: self.module = v
                case 'arguments' | self.___websystem_configs___.url_key_arguments: self.arguments = v
                case 'keyword' | self.___websystem_configs___.url_key_keyword: self.keyword = v
                case 'page' | self.___websystem_configs___.url_key_page: self.page = v
                case 'orders' | self.___websystem_configs___.url_key_orders: self.orders = v
                case 'filters' | self.___websystem_configs___.url_key_filters: self.filters = v
                case 'items_per_page' | self.___websystem_configs___.url_key_items_per_page: self.items_per_page = v
                case 'pages_per_group' | self.___websystem_configs___.url_key_pages_per_group: self.pages_per_group = v
                case 'reference' | self.___websystem_configs___.url_key_reference: self.reference = v
                case 'language' | self.___websystem_configs___.url_key_language: self.language = v
                case 'security' | self.___websystem_configs___.url_key_security: self.security = v

    def data(self):
        cs = self.___websystem_configs___
        data: dict = {
            cs.url_key_mode: self.mode,
            cs.url_key_language: self.language,
            cs.url_key_module: self.module
        }
        if self.arguments:
            # data[self.___cr___.url_key_arguments] = json.dumps(self.arguments)
            data[cs.url_key_arguments] = self.arguments
        if self.keyword is not None:
            data[cs.url_key_keyword] = self.keyword
            data[cs.url_key_page] = self.page
            if self.orders:
                data[cs.url_key_orders] = self.orders
            else:
                data[cs.url_key_orders] = {}
            if self.filters:
                data[cs.url_key_filters] = self.filters
            else:
                data[cs.url_key_filters] = {}
            if self.items_per_page:
                data[cs.url_key_items_per_page] = self.items_per_page
            else:
                data[cs.url_key_items_per_page] = cs.pagination_items_per_page
            if self.pages_per_group:
                data[cs.url_key_pages_per_group] = self.pages_per_group
            else:
                data[cs.url_key_pages_per_group] = cs.pagination_pages_per_group
        if self.reference:
            data[cs.url_key_reference] = self.reference
        if self.security:
            data[cs.url_key_security] = self.security
        return data

    def redirect(self): return self.__client__.__websystem__.server.make_response_redirect(self.output())

    # def __str__(self): return self.data().__str__()