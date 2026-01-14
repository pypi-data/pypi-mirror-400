import re

from ......functions.builtins import import_webapp_pycls_by_mod_path
from ......functions.decorators import parse_self_x_item_value_or_set_by_func, \
    parse_self_x_item_value_or_set_by_instance_he_by_module_name
from .....types.hs import Hs


class Webmod(Hs):
    def __init__(self, u, fullname: str):
        super().__init__(u, fullname)
        self.__x__['fullname'] = fullname

    @property
    def websystem(self): return self.website.websystem
    """@property
    def server(self): return self.websystem.server"""
    @property
    def website(self): return self.__u__
    """@property
    def client(self): return self.website.client
    @property
    def database(self): return self.websystem.database"""

    def webmod(self, *names: str): return self.website.webmod(*names)
    @property
    def webmod_home(self): return self.webmod()
    @property
    def webmod_page_content_sign_in(self): return self.webmod(self.websystem.configs.webmod_page_content_sign_in)
    @property
    def webmod_page_content_sign_out(self): return self.webmod(self.websystem.configs.webmod_page_content_sign_out)
    @property
    def webmod_page_content_sign_up(self): return self.webmod(self.websystem.configs.webmod_page_content_sign_up)
    @property
    def webmod_page_content_about(self): return self.webmod(self.websystem.configs.webmod_page_content_about)
    @property
    def webmod_page_content_contact(self): return self.webmod(self.websystem.configs.webmod_page_content_contact)
    @property
    def webmod_page_content_admin(self): return self.webmod(self.websystem.configs.webmod_page_content_admin)

    @property
    def webmod_page_layout(self): return self.webmod(self.websystem.configs.webmod_page_layout)
    @property
    def webmod_page_block_navbar(self): return self.webmod(self.websystem.configs.webmod_page_block_navbar)
    @property
    def webmod_page_block_breadcrumb(self): return self.webmod(self.websystem.configs.webmod_page_block_breadcrumb)
    @property
    def webmod_page_block_navigations(self): return self.webmod(self.websystem.configs.webmod_page_block_navigations)
    @property
    def webmod_page_block_messages(self): return self.webmod(self.websystem.configs.webmod_page_block_messages)
    @property
    def webmod_page_block_footer(self): return self.webmod(self.websystem.configs.webmod_page_block_footer)
    @property
    def webmod_page_block_debugs(self): return self.webmod(self.websystem.configs.webmod_page_block_debugs)

    # 按照 setting 中 serial 排序
    def search_children_webmods(self):
        return [self.child_webmod(i) for i in self.folder.search_usable_children_folder_names()]
        # return sorted([self.child_webmod(i) for i in self.folder.search_usable_children_folder_names()], key=lambda i: i.settings.serial)
    def search_children_webmods_by_page_featur_general(self):
        return [i for i in self.search_children_webmods() if i.settings.is_page_feature_general()]

    def has_page_iterative(self): return self.has_local_method('page_iterative')
    def has_page_content(self): return self.has_local_method('page_content')
    def has_page_layout(self): return self.has_local_method('page_layout')
    def has_page_block_navbar(self): return self.has_local_method('page_block_navbar')
    def has_page_block_breadcrumb(self): return self.has_local_method('page_block_breadcrumb')
    def has_page_block_navigations(self): return self.has_local_method('page_block_navigations')
    def has_page_block_messages(self): return self.has_local_method('page_block_messages')
    def has_page_block_footer(self): return self.has_local_method('page_block_footer')
    def has_page_block_debugs(self): return self.has_local_method('page_block_debugs')
    def has_page_block_1010(self): return self.has_local_method('page_block_1010')
    def has_page_block_1020(self): return self.has_local_method('page_block_1020')
    def has_page_block_1030(self): return self.has_local_method('page_block_1030')
    def has_page_block_1040(self): return self.has_local_method('page_block_1040')
    def has_page_block_1050(self): return self.has_local_method('page_block_1050')
    def has_page_block_1060(self): return self.has_local_method('page_block_1060')
    def has_page_block_1070(self): return self.has_local_method('page_block_1070')
    def has_page_block_1080(self): return self.has_local_method('page_block_1080')
    def has_page_block_1090(self): return self.has_local_method('page_block_1090')
    def has_page_block_1100(self): return self.has_local_method('page_block_1100')

    @property
    @parse_self_x_item_value_or_set_by_func()
    def senior(self): return None if self.is_root() else self.webmod(*self.split('.')[:-1])

    def child_webmod(self, *names): return self.website.webmod(self, *names) if names else None

    @property
    @parse_self_x_item_value_or_set_by_func()
    def name(self): return self.tree_names[-1]
    @parse_self_x_item_value_or_set_by_func()
    def is_name_serialized(self): return bool(re.match(r'^n\d+_', self.name))
    @property
    @parse_self_x_item_value_or_set_by_func()
    def net_name(self): return self.name.split('_', 1)[-1] if self.is_name_serialized() else self.name
    @property
    @parse_self_x_item_value_or_set_by_func()
    def tree_names(self): return self.split('.')

    @property
    @parse_self_x_item_value_or_set_by_func()
    def fullname(self): return

    def is_root(self): return self == ''

    @property
    @parse_self_x_item_value_or_set_by_func()
    def tree(self): return [self] if self.is_root() else [*self.senior.tree, self]

    @property
    @parse_self_x_item_value_or_set_by_func()
    def mod_path(self): return self.__sm__.mod_path(self.websystem.configs.module if self.is_root() else '.'.join([self.websystem.configs.module, self.fullname]))
    @property
    def mod_type(self): return self.mod_path.mod_type
    def is_mod_exists(self): return self.mod_type.pymod is not None
    @property
    @parse_self_x_item_value_or_set_by_func()
    def cls_type(self):
        try: return self.__sm__.cls_type(import_webapp_pycls_by_mod_path(self.mod_path))
        except: return None
    def is_cls_exists(self): return self.cls_type is not None
    def has_local_method(self, name): return self.is_cls_exists() and callable(self.cls_type.pycls.__dict__.get(name))

    @property
    @parse_self_x_item_value_or_set_by_func()
    def obj_type(self):
        if self.is_cls_exists():
            try: return self.__sm__.obj_type(self.cls_type.pycls(self))
            except: pass
        return None
    def is_object_instantiated(self): return self.obj_type is not None

    @property
    def folder(self): return self.websystem.website_folder if self.is_root() else self.senior.folder.child_folder(self.name)
    def is_folder_exists(self): return self.folder.is_exists()
    def folder_child_file(self, name: str | list[str]): return self.folder.child_file(name)
    def folder_child_folder(self, name: str | list[str]): return self.folder.child_folder(name)

    @property
    @parse_self_x_item_value_or_set_by_func()
    def data_folder(self): return self.folder.child_folder(self.__si__.DIRNAM_DATA)
    def data_folder_child_file(self, name: str | list[str]): return self.data_folder.child_file(name)
    def data_folder_child_folder(self, name: str | list[str]): return self.data_folder.child_folder(name)
    @property
    @parse_self_x_item_value_or_set_by_func()
    def data_configs_folder(self): return self.data_folder.child_folder(self.__si__.DIRNAM_DATA_CONFIGS)
    @property
    @parse_self_x_item_value_or_set_by_func()
    def data_configs_file(self): return self.data_configs_folder.child_file(self.__si__.FILNAM_CONFIGS)
    @property
    @parse_self_x_item_value_or_set_by_func()
    def data_settings_folder(self): return self.data_folder.child_folder(self.__si__.DIRNAM_DATA_SETTINGS)
    @property
    @parse_self_x_item_value_or_set_by_func()
    def data_settings_file(self): return self.data_settings_folder.child_file(self.__si__.FILNAM_SETTINGS)
    @property
    @parse_self_x_item_value_or_set_by_func()
    def data_database_tables_folder(self): return self.data_folder.child_folder(self.__si__.DIRNAM_DATA_DATABASE_TABLES)
    @property
    @parse_self_x_item_value_or_set_by_func()
    def data_database_data_folder(self): return self.data_folder.child_folder(self.__si__.DIRNAM_DATA_DATABASE_DATA)
    @property
    @parse_self_x_item_value_or_set_by_func()
    def data_multilinguals_folder(self): return self.data_folder.child_folder(self.__si__.DIRNAM_DATA_MULTILINGALS)
    def data_multilinguals_file(self, language: str): return self.data_multilinguals_folder.child_file(f'{language}.json')
    @property
    @parse_self_x_item_value_or_set_by_func()
    def logs_folder(self): return self.data_folder.child_folder(self.__si__.DIRNAM_LOGS)
    @property
    @parse_self_x_item_value_or_set_by_func()
    def public_folder(self): return self.data_folder.child_folder(self.__si__.DIRNAM_PUBLIC)
    def public_folder_child_file(self, name: str | list[str]): return self.public_folder.child_file(name)
    def public_folder_child_folder(self, name: str | list[str]): return self.public_folder.child_folder(name)
    @property
    @parse_self_x_item_value_or_set_by_instance_he_by_module_name()
    def multilinguals(self): return
    @property
    @parse_self_x_item_value_or_set_by_func()
    def ___ml_by_webmod_name___(self): return ' '.join([i.capitalize() for i in self.net_name.split('_') if i])
    def ml(self, code, language=None, replace=None, return_code=True): return (r:=self.multilinguals.ml(code, language, replace, False)) or (self.___ml_by_webmod_name___ if return_code else r)
    def ml_name(self, language=None, replace=None, return_code=True): return (r:=self.multilinguals.ml_name(language, replace, False)) or (self.___ml_by_webmod_name___ if return_code else r)
    def ml_abbreviation(self, language=None, replace=None, return_code=True): return (r:=self.multilinguals.ml_abbreviation(language, replace, False)) or (self.___ml_by_webmod_name___ if return_code else r)
    def ml_title(self, language=None, replace=None, return_code=True): return (r:=self.multilinguals.ml_title(language, replace, False)) or (self.___ml_by_webmod_name___ if return_code else r)
    def ml_description(self, language=None, replace=None, return_code=True): return (r:=self.multilinguals.ml_description(language, replace, False)) or (self.___ml_by_webmod_name___ if return_code else r)
    def ml_link_title(self, language=None, replace=None, return_code=True): return (r:=self.multilinguals.ml_link_title(language, replace, False)) or (self.___ml_by_webmod_name___ if return_code else r)
    def ml_page_title(self, language=None, replace=None, return_code=True): return (r:=self.multilinguals.ml_page_title(language, replace, False)) or (self.___ml_by_webmod_name___ if return_code else r)
    def ml_breadcrumb_title(self, language=None, replace=None, return_code=True): return (r:=self.multilinguals.ml_breadcrumb_title(language, replace, False)) or (self.___ml_by_webmod_name___ if return_code else r)

    @property
    def htmdoc(self): return self.website.htmdoc

    @property
    def page_areas(self): return self.website.htmdoc.areas

    @property
    def page_area_content(self): return self.website.htmdoc.areas.content
    @property
    def page_area_navbar(self): return self.website.htmdoc.areas.navbar
    @property
    def page_area_breadcrumb(self): return self.website.htmdoc.areas.breadcrumb
    @property
    def page_area_navigations(self): return self.website.htmdoc.areas.navigations
    @property
    def page_area_messages(self): return self.website.htmdoc.areas.messages
    @property
    def page_area_footer(self): return self.website.htmdoc.areas.footer
    @property
    def page_area_debugs(self): return self.website.htmdoc.areas.debugs

    def __execute__(self, name):
        # getattr(self.pyobject, name)(); return True
        if self.is_object_instantiated():
            if self.is_object_instantiated():
                # getattr(self.pyobject, name)(); return True
                try: getattr(self.obj_type, name)(); return True
                except Exception as e: self.websystem.server.__deubg_warning__(f'运行模块失败', e, f'{self.mod_path}.core.Core().{name}()', __file__)
        return False

    def execute_page_iterative(self):
        for m in self.tree:
            if m.has_page_iterative():
                if not m.__execute__('page_iterative'):
                    return False
        return True
    def execute_page_content(self): return self.__execute__('page_content')
    def execute_page_layout(self): return self.__execute__('page_layout')
    def execute_page_block_navbar(self): return self.__execute__('page_block_navbar')
    def execute_page_block_breadcrumb(self): return self.__execute__('page_block_breadcrumb')
    def execute_page_block_navigations(self): return self.__execute__('page_block_navigations')
    def execute_page_block_messages(self): return self.__execute__('page_block_messages')
    def execute_page_block_footer(self): return self.__execute__('page_block_footer')
    def execute_page_block_debugs(self): return self.__execute__('page_block_debugs')
    def execute_page_block_1010(self): return self.__execute__('page_block_1010')
    def execute_page_block_1020(self): return self.__execute__('page_block_1020')
    def execute_page_block_1030(self): return self.__execute__('page_block_1030')
    def execute_page_block_1040(self): return self.__execute__('page_block_1040')
    def execute_page_block_1050(self): return self.__execute__('page_block_1050')
    def execute_page_block_1060(self): return self.__execute__('page_block_1060')
    def execute_page_block_1070(self): return self.__execute__('page_block_1070')
    def execute_page_block_1080(self): return self.__execute__('page_block_1080')
    def execute_page_block_1090(self): return self.__execute__('page_block_1090')
    def execute_page_block_1100(self): return self.__execute__('page_block_1100')

    def address(self, mode=None, arguments=None, keyword=None, page=None, orders=None, filters=None, items_per_page=None, pages_per_group=None, reference=None, language=None, security=None): return self.website.client.address(mode, self.fullname, arguments, keyword, page, orders, filters, items_per_page, pages_per_group, reference, language, security)
    def url(self, mode=None, arguments=None, keyword=None, page=None, orders=None, filters=None, items_per_page=None, pages_per_group=None, reference=None, language=None, security=None): return self.address(mode, arguments, keyword, page, orders, filters, items_per_page, pages_per_group, reference, language, security).output()
    def redirect(self, mode=None, arguments=None, keyword=None, page=None, orders=None, filters=None, items_per_page=None, pages_per_group=None, reference=None, language=None, security=None): return self.address(mode, arguments, keyword, page, orders, filters, items_per_page, pages_per_group, reference, language, security).redirect()

    def page_address(self, arguments=None, keyword=None, page=None, orders=None, filters=None, items_per_page=None, pages_per_group=None, reference=None, language=None, security=None): return self.address('page', arguments, keyword, page, orders, filters, items_per_page, pages_per_group, reference, language, security)
    def page_url(self, arguments=None, keyword=None, page=None, orders=None, filters=None, items_per_page=None, pages_per_group=None, reference=None, language=None, security=None): return self.page_address(arguments, keyword, page, orders, filters, items_per_page, pages_per_group, reference, language, security).output()
    def page_redirect(self, arguments=None, keyword=None, page=None, orders=None, filters=None, items_per_page=None, pages_per_group=None, reference=None, language=None, security=None): return self.page_address(arguments, keyword, page, orders, filters, items_per_page, pages_per_group, reference, language, security).redirect()


    def address_by_current(self): return self.website.client.request.address.copy()
    def url_by_current(self): return self.address_by_current().output()
    def address_by_current_change_language(self, language=None):
        a = self.address_by_current()
        a.language = language
        return a
    def url_by_current_change_language(self, language=None): return self.address_by_current_change_language(language).output()
    def address_by_current_change_pagination(self, keyword=None, page=None, orders=None, filters=None, items_per_page=None, pages_per_group=None):
        a = self.address_by_current()
        if keyword is not None: a.keyword = keyword
        a.page, a.orders, a.filters, a.items_per_page, a.pages_per_group = page, orders, filters, items_per_page, pages_per_group
        return a
    def url_by_current_change_pagination(self, keyword=None, page=None, orders=None, filters=None, items_per_page=None, pages_per_group=None): return self.address_by_current_change_pagination(keyword, page, orders, filters, items_per_page, pages_per_group).output()

    def set_page_navbar_logo(self, url): return
    def add_page_breadcrumb(self, title=None, url=None): self.htmdoc.caches.breadcrumb.add_menu(title, url)

    def public_file_url(self, *names: str): return self.websystem.server.generate_url(*self.split('.'), self.__si__.DIRNAM_PUBLIC, *names)

    @property
    @parse_self_x_item_value_or_set_by_instance_he_by_module_name()
    def settings(self): return

    def is_active_by_client(self): return self.website.client.request.address.module == self
