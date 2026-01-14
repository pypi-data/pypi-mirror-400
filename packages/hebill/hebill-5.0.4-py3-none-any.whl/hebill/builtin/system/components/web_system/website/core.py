import os.path

from .....functions.builtins import join_url, decompress
from .....functions.decorators import parse_self_x_item_value_or_set_by_func, parse_self_x_item_value, \
    parse_self_x_item_value_or_set_by_instance_he_by_module_name
from ....types.hd import Hd


class Website(Hd):
    def __init__(self, websystem, client):
        super().__init__(websystem)
        self.__x__['client'] = client

    @property
    @parse_self_x_item_value_or_set_by_func()
    def websystem(self): return self.__u__
    @property
    @parse_self_x_item_value()
    def client(self): return

    """@property
    @parse_self_x_item_value_or_set_by_instance_he_by_module_name()
    def html_document(self): return"""

    @property
    @parse_self_x_item_value_or_set_by_instance_he_by_module_name()
    def htmdoc(self): return

    @property
    def favicon_ico_url_path(self): return join_url('/', self.websystem.configs.url_root_path, 'favicon.ico')

    def webmod(self, *names: str):
        ns = [n for i in names if (n:=i.strip('.'))]
        from .webmod import Webmod
        return Webmod(self, '.'.join(ns) if ns else '')

    @property
    def webroot(self): return self.webmod()

    def address(self, mode=None, module=None, arguments=None, keyword=None, page=None, orders=None, filters=None, items_per_page=None, pages_per_group=None, reference=None, language=None, security=None): return self.client.address(mode, module, arguments, keyword, page, orders, filters, items_per_page, pages_per_group, reference, language, security)
    def url(self, mode=None, module=None, arguments=None, keyword=None, page=None, orders=None, filters=None, items_per_page=None, pages_per_group=None, reference=None, language=None, security=None): return self.address(mode, module, arguments, keyword, page, orders, filters, items_per_page, pages_per_group, reference, language, security).output()
    def redirect(self, mode=None, module=None, arguments=None, keyword=None, page=None, orders=None, filters=None, items_per_page=None, pages_per_group=None, reference=None, language=None, security=None): return self.address(mode, module, arguments, keyword, page, orders, filters, items_per_page, pages_per_group, reference, language, security).redirect()

    def response(self):
        si = self.__si__
        got_path_names = [i for i in self.client.request.path.strip(' /').split('/') if i]
        print('排查', 100, 'got_path_names', got_path_names)
        rel_path_names = [i for i in self.websystem.configs.url_root_path.strip(' /').split('/') if i]
        print('排查', 200, 'rel_path_names', rel_path_names)
        if len(got_path_names) < len(rel_path_names) or got_path_names[:len(rel_path_names)] != rel_path_names:
            return self.websystem.server.make_response_404()
        if len(rel_path_names) > 0: act_path_names = got_path_names[:len(rel_path_names)]
        else: act_path_names = got_path_names
        print('排查', 300, 'rel_path_names', rel_path_names)
        def response_favicon():
            if (i:= self.webroot.folder.child_file('logo.ico')).is_exists(): return self.websystem.server.make_response_file(i)
            if (i:= si.folder.child_file('logo.ico')).is_exists(): return self.websystem.server.make_response_file(i)
            return self.websystem.server.make_response_404()
        def response_cdn():
            if (i:=si.cdn_folder.child_file(*act_path_names[1:])).is_exists(): return self.websystem.server.make_response_file(i)
            return self.websystem.server.make_response_404()
        def response_pub():
            if (i:=self.webroot.folder.child_file(*act_path_names[1:])).is_exists(): return self.websystem.server.make_response_file(i)
            return self.websystem.server.make_response_404()
        def parse_requested_parameters():
            self.client.request.address.language = act_path_names[0]
            try: a = decompress(act_path_names[1])
            except: a = {}
            if not isinstance(a, dict): a = {}
            self.client.request.address.language = a.get(self.websystem.configs.url_key_language, self.websystem.configs.language)
            self.client.request.address.module = a.get(self.websystem.configs.url_key_module, '')
            self.client.request.address.arguments = a.get(self.websystem.configs.url_key_arguments, {})
            self.client.request.address.keyword = a.get(self.websystem.configs.url_key_keyword, None)
            self.client.request.address.page = a.get(self.websystem.configs.url_key_page, 1)
            self.client.request.address.orders = a.get(self.websystem.configs.url_key_orders, {})
            self.client.request.address.filters = a.get(self.websystem.configs.url_key_filters, {})
            self.client.request.address.items_per_page = a.get(self.websystem.configs.url_key_items_per_page, self.websystem.configs.pagination_items_per_page)
            self.client.request.address.pages_per_group = a.get(self.websystem.configs.url_key_pages_per_group, self.websystem.configs.pagination_pages_per_group)
            self.client.request.address.reference = a.get(self.websystem.configs.url_key_reference, '')
            self.client.request.address.security = a.get(self.websystem.configs.url_key_security, '')
            self.client.request.arguments.update(a.get(self.websystem.configs.url_key_arguments, {}))

        def response_pag():
            self.websystem.server.__deubg_info__(f'请求页面[{self.client.request.method}]: [{self.client.request.address.module or '/'}] <=> {self.client.request.url}')
            # 运行模板
            m = self.webmod(self.client.request.address.module)
            mod_lay = m.settings['page_layout'] or self.websystem.configs['webmod_page_layout']
            if mod_lay == '#': mod_lay = str(m)
            if not self.webmod(mod_lay).execute_page_layout():
                self.webroot.execute_page_layout()
            # 运行内容，错误返回错误模块
            # 权限限制： 401，页面找不到：404，运行错误：500，建设中：501
            power = True
            def execute_page():
                if m.is_folder_exists():
                    if power:
                        if m.is_mod_exists():
                            if m.is_cls_exists():
                                if m.is_object_instantiated():
                                    if (result := m.obj_type.pyobj.page_content()) is not None: return result
                                    """try: return rst if (rst:=m.pyobject.page_content()) is not None else None
                                    except: self.webmod(self.websystem.configs.webmod_page_block_1100).execute_page_block_1100()"""
                                    return None
                                self.webmod(self.websystem.configs.webmod_page_block_1090).execute_page_block_1090()
                                return None
                            self.webmod(self.websystem.configs.webmod_page_block_1080).execute_page_block_1080()
                            return None
                        self.webmod(self.websystem.configs.webmod_page_block_1070).execute_page_block_1070()
                        return None
                    self.webmod(self.websystem.configs.webmod_page_block_1060).execute_page_block_1060()
                    return None
                self.webmod(self.websystem.configs.webmod_page_block_1050).execute_page_block_1050()
                return None

            executed = execute_page()
            if executed is not None: return executed
            return self.websystem.server.make_response_text_html(self.htmdoc.output())
        print('排查', 1100, 'act_path_names', act_path_names)
        if len(act_path_names) == 0: act_path_names = [si.WEBMOD_PAG]
        print('排查', 1200, 'act_path_names', act_path_names)
        if act_path_names[0] == 'favicon.ico': return response_favicon()
        print('排查', 1300, 'act_path_names', act_path_names)
        match act_path_names[0]:
            case si.WEBMOD_CDN:
                print('排查', 2100, 'act_path_names', act_path_names)
                return response_cdn()
            case si.WEBMOD_PUB:
                print('排查', 2200, 'act_path_names', act_path_names)
                return response_pub()
            case si.WEBMOD_AJX | si.WEBMOD_FIL | si.WEBMOD_LAY | si.WEBMOD_JSN | si.WEBMOD_PAG | si.WEBMOD_STM:
                print('排查', 2300, 'act_path_names', act_path_names)
                parse_requested_parameters()
                match act_path_names[0]:
                    case si.WEBMOD_AJX: # TODO
                        print('排查', 3100, 'act_path_names', act_path_names)
                        return self.websystem.server.make_response_text_plain('这里是请求的 Ajax 內容')
                    case si.WEBMOD_FIL: # TODO
                        print('排查', 3200, 'act_path_names', act_path_names)
                        return self.websystem.server.make_response_text_plain('这里是请求的 File 內容')
                    case si.WEBMOD_LAY: # TODO
                        print('排查', 3300, 'act_path_names', act_path_names)
                        return self.websystem.server.make_response_text_plain('这里是请求的 Layout 內容')
                    case si.WEBMOD_JSN: # TODO
                        print('排查', 3400, 'act_path_names', act_path_names)
                        return self.websystem.server.make_response_text_plain('这里是请求的 Json 內容')
                    case si.WEBMOD_PAG:
                        print('排查', 3500, 'act_path_names', act_path_names)
                        return response_pag()
                    case si.WEBMOD_STM: # TODO
                        print('排查', 3600, 'act_path_names', act_path_names)
                        return self.websystem.server.make_response_text_plain('这里是请求的 Steam 內容')
            case _:
                print('排查', 3400, 'act_path_names', act_path_names)
                return self.websystem.server.make_response_404()
