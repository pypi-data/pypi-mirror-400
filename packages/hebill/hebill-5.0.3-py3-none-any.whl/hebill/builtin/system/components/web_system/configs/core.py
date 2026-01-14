from .....functions.decorators import parse_self_item_value, set_self_item_value_by_setter_with_agr
from ...configs import Configs as ModConfigs


class Configs(ModConfigs):
    def __init__(self, system):
        super().__init__(system)
        self.update({
            "server": "flask",

            "session_expiry": 86400,

            'language': self.__sc__['language'],
            'host': '0.0.0.0',
            'port': 5000,
            'module': 'hebill.website',

            "mysql_host": "",
            "mysql_port": 3306,
            "mysql_user": "",
            "mysql_password": "",
            "mysql_dbname": "",
            "mysql_prefix": "",

            "mysql_max_connections": 30,
            "mysql_connect_timeout": 5,
            "mysql_column_key_sn": "_sn",
            "mysql_column_key_id": "_id",
            "mysql_column_key_az": "_az",
            "mysql_column_key_kw": "_kw",
            "mysql_column_key_ur": "_ur",
            "mysql_column_key_dc": "_dc",
            "mysql_column_key_du": "_du",
            "mysql_data_admin_id": "_admin",

            'webmod_page_content_sign_in': 'sign_in',
            'webmod_page_content_sign_out': 'sign_out',
            'webmod_page_content_sign_up': 'sign_up',
            'webmod_page_content_sign_reset': 'sign_reset',
            'webmod_page_content_about': 'about',
            'webmod_page_content_contact': 'contact',
            'webmod_page_content_admin': 'admin',

            'webmod_page_layout': '',

            'webmod_page_block_1010': '',
            'webmod_page_block_1020': '',
            'webmod_page_block_1030': '',
            'webmod_page_block_1040': '',
            'webmod_page_block_1050': '',
            'webmod_page_block_1060': '',
            'webmod_page_block_1070': '',
            'webmod_page_block_1080': '',
            'webmod_page_block_1090': '',
            'webmod_page_block_1100': '',

            'webmod_page_block_navbar': '',
            'webmod_page_block_breadcrumb': '',
            'webmod_page_block_navigations': '',
            'webmod_page_block_messages': '',
            'webmod_page_block_footer': '',
            'webmod_page_block_debugs': '',

            'html_output_minimized': False,
            'html_output_unspaced': False,
            'html_output_comments': True,
            'html_output_indentation': '\t',
            'html_title_delimiter': '/',
            'html_title_ascending': True,

            "url_root_path": "",

            "url_key_language": "l",
            "url_key_mode": "t",
            "url_key_module": "m",
            "url_key_arguments": "a",
            "url_key_keyword": "k",
            "url_key_page": "n",
            "url_key_orders": "o",
            "url_key_filters": "f",
            "url_key_items_per_page": "i",
            "url_key_pages_per_group": "g",
            "url_key_security": "s",
            "url_key_reference": "r",

            "pagination_items_per_page": 25,
            "pagination_pages_per_group": 10,

            "logo": "",
        })

    @property
    @parse_self_item_value()
    def language(self): return
    @language.setter
    @set_self_item_value_by_setter_with_agr(value_type='lan')
    def language(self, value): pass

    @property
    @parse_self_item_value()
    def session_expiry(self): return
    @session_expiry.setter
    @set_self_item_value_by_setter_with_agr(value_type='intp')
    def session_expiry(self, value): pass

    @property
    @parse_self_item_value()
    def host(self): return
    @host.setter
    @set_self_item_value_by_setter_with_agr(value_type='strue')
    def host(self, value): pass

    @property
    @parse_self_item_value()
    def port(self): return
    @port.setter
    @set_self_item_value_by_setter_with_agr(value_type='intp')
    def port(self, value): pass

    @property
    @parse_self_item_value()
    def mysql_host(self): return
    @mysql_host.setter
    @set_self_item_value_by_setter_with_agr(value_type='strue')
    def mysql_host(self, value): pass

    @property
    @parse_self_item_value()
    def mysql_port(self): return
    @mysql_port.setter
    @set_self_item_value_by_setter_with_agr(value_type='intp')
    def mysql_port(self, value): pass

    @property
    @parse_self_item_value()
    def mysql_user(self): return
    @mysql_user.setter
    @set_self_item_value_by_setter_with_agr(value_type='strue')
    def mysql_user(self, value): pass

    @property
    @parse_self_item_value()
    def mysql_password(self): return
    @mysql_password.setter
    @set_self_item_value_by_setter_with_agr(value_type='strue')
    def mysql_password(self, value): pass

    @property
    @parse_self_item_value()
    def mysql_dbname(self): return
    @mysql_dbname.setter
    @set_self_item_value_by_setter_with_agr(value_type='strue')
    def mysql_dbname(self, value): pass

    @property
    @parse_self_item_value()
    def mysql_prefix(self): return
    @mysql_prefix.setter
    @set_self_item_value_by_setter_with_agr(value_type='strue')
    def mysql_prefix(self, value): pass

    @property
    @parse_self_item_value()
    def mysql_max_connections(self): return
    @mysql_max_connections.setter
    @set_self_item_value_by_setter_with_agr(value_type='intp')
    def mysql_max_connections(self, value): pass

    @property
    @parse_self_item_value()
    def mysql_connect_timeout(self): return
    @mysql_connect_timeout.setter
    @set_self_item_value_by_setter_with_agr(value_type='intp')
    def mysql_connect_timeout(self, value): pass

    @property
    @parse_self_item_value()
    def mysql_column_key_sn(self): return
    @mysql_column_key_sn.setter
    @set_self_item_value_by_setter_with_agr(value_type='strue')
    def mysql_column_key_sn(self, value): pass

    @property
    @parse_self_item_value()
    def mysql_column_key_id(self): return
    @mysql_column_key_id.setter
    @set_self_item_value_by_setter_with_agr(value_type='strue')
    def mysql_column_key_id(self, value): pass

    @property
    @parse_self_item_value()
    def mysql_column_key_az(self): return
    @mysql_column_key_az.setter
    @set_self_item_value_by_setter_with_agr(value_type='strue')
    def mysql_column_key_az(self, value): pass

    @property
    @parse_self_item_value()
    def mysql_column_key_kw(self): return
    @mysql_column_key_kw.setter
    @set_self_item_value_by_setter_with_agr(value_type='strue')
    def mysql_column_key_kw(self, value): pass

    @property
    @parse_self_item_value()
    def mysql_column_key_ur(self): return
    @mysql_column_key_ur.setter
    @set_self_item_value_by_setter_with_agr(value_type='strue')
    def mysql_column_key_ur(self, value): pass

    @property
    @parse_self_item_value()
    def mysql_column_key_dc(self): return
    @mysql_column_key_dc.setter
    @set_self_item_value_by_setter_with_agr(value_type='strue')
    def mysql_column_key_dc(self, value): pass

    @property
    @parse_self_item_value()
    def mysql_column_key_du(self): return
    @mysql_column_key_du.setter
    @set_self_item_value_by_setter_with_agr(value_type='strue')
    def mysql_column_key_du(self, value): pass

    @property
    @parse_self_item_value()
    def mysql_data_admin_id(self): return
    @mysql_data_admin_id.setter
    @set_self_item_value_by_setter_with_agr(value_type='strue')
    def mysql_data_admin_id(self, value): pass

    @property
    @parse_self_item_value()
    def module(self): return
    @module.setter
    @set_self_item_value_by_setter_with_agr(value_type='strue')
    def module(self, value): pass

    @property
    @parse_self_item_value()
    def webmod_page_content_sign_in(self): return
    @webmod_page_content_sign_in.setter
    @set_self_item_value_by_setter_with_agr(value_type='str')
    def webmod_page_content_sign_in(self, value): pass

    @property
    @parse_self_item_value()
    def webmod_page_content_sign_out(self): return
    @webmod_page_content_sign_out.setter
    @set_self_item_value_by_setter_with_agr(value_type='str')
    def webmod_page_content_sign_out(self, value): pass

    @property
    @parse_self_item_value()
    def webmod_page_content_sign_up(self): return
    @webmod_page_content_sign_up.setter
    @set_self_item_value_by_setter_with_agr(value_type='str')
    def webmod_page_content_sign_up(self, value): pass

    @property
    @parse_self_item_value()
    def webmod_page_content_sign_reset(self): return
    @webmod_page_content_sign_reset.setter
    @set_self_item_value_by_setter_with_agr(value_type='str')
    def webmod_page_content_sign_reset(self, value): pass

    @property
    @parse_self_item_value()
    def webmod_page_content_admin(self): return
    @webmod_page_content_admin.setter
    @set_self_item_value_by_setter_with_agr(value_type='str')
    def webmod_page_content_admin(self, value): pass

    @property
    @parse_self_item_value()
    def webmod_page_content_about(self): return
    @webmod_page_content_about.setter
    @set_self_item_value_by_setter_with_agr(value_type='str')
    def webmod_page_content_about(self, value): pass

    @property
    @parse_self_item_value()
    def webmod_page_content_contact(self): return
    @webmod_page_content_contact.setter
    @set_self_item_value_by_setter_with_agr(value_type='str')
    def webmod_page_content_contact(self, value): pass

    @property
    @parse_self_item_value()
    def webmod_page_layout(self): return
    @webmod_page_layout.setter
    @set_self_item_value_by_setter_with_agr(value_type='str')
    def webmod_page_layout(self, value): pass

    @property
    @parse_self_item_value()
    def webmod_page_block_1010(self): return
    @webmod_page_block_1010.setter
    @set_self_item_value_by_setter_with_agr(value_type='str')
    def webmod_page_block_1010(self, value): pass

    @property
    @parse_self_item_value()
    def webmod_page_block_1020(self): return
    @webmod_page_block_1020.setter
    @set_self_item_value_by_setter_with_agr(value_type='str')
    def webmod_page_block_1020(self, value): pass

    @property
    @parse_self_item_value()
    def webmod_page_block_1030(self): return
    @webmod_page_block_1030.setter
    @set_self_item_value_by_setter_with_agr(value_type='str')
    def webmod_page_block_1030(self, value): pass

    @property
    @parse_self_item_value()
    def webmod_page_block_1040(self): return
    @webmod_page_block_1040.setter
    @set_self_item_value_by_setter_with_agr(value_type='str')
    def webmod_page_block_1040(self, value): pass

    @property
    @parse_self_item_value()
    def webmod_page_block_1050(self): return
    @webmod_page_block_1050.setter
    @set_self_item_value_by_setter_with_agr(value_type='str')
    def webmod_page_block_1050(self, value): pass

    @property
    @parse_self_item_value()
    def webmod_page_block_1060(self): return
    @webmod_page_block_1060.setter
    @set_self_item_value_by_setter_with_agr(value_type='str')
    def webmod_page_block_1060(self, value): pass

    @property
    @parse_self_item_value()
    def webmod_page_block_1070(self): return
    @webmod_page_block_1070.setter
    @set_self_item_value_by_setter_with_agr(value_type='str')
    def webmod_page_block_1070(self, value): pass

    @property
    @parse_self_item_value()
    def webmod_page_block_1080(self): return
    @webmod_page_block_1080.setter
    @set_self_item_value_by_setter_with_agr(value_type='str')
    def webmod_page_block_1080(self, value): pass

    @property
    @parse_self_item_value()
    def webmod_page_block_1090(self): return
    @webmod_page_block_1090.setter
    @set_self_item_value_by_setter_with_agr(value_type='str')
    def webmod_page_block_1090(self, value): pass

    @property
    @parse_self_item_value()
    def webmod_page_block_1100(self): return
    @webmod_page_block_1100.setter
    @set_self_item_value_by_setter_with_agr(value_type='str')
    def webmod_page_block_1100(self, value): pass

    @property
    @parse_self_item_value()
    def webmod_page_block_navbar(self): return
    @webmod_page_block_navbar.setter
    @set_self_item_value_by_setter_with_agr(value_type='str')
    def webmod_page_block_navbar(self, value): pass

    @property
    @parse_self_item_value()
    def webmod_page_block_breadcrumb(self): return
    @webmod_page_block_breadcrumb.setter
    @set_self_item_value_by_setter_with_agr(value_type='str')
    def webmod_page_block_breadcrumb(self, value): pass

    @property
    @parse_self_item_value()
    def webmod_page_block_navigations(self): return
    @webmod_page_block_navigations.setter
    @set_self_item_value_by_setter_with_agr(value_type='str')
    def webmod_page_block_navigations(self, value): pass

    @property
    @parse_self_item_value()
    def webmod_page_block_messages(self): return
    @webmod_page_block_messages.setter
    @set_self_item_value_by_setter_with_agr(value_type='str')
    def webmod_page_block_messages(self, value): pass

    @property
    @parse_self_item_value()
    def webmod_page_block_footer(self): return
    @webmod_page_block_footer.setter
    @set_self_item_value_by_setter_with_agr(value_type='str')
    def webmod_page_block_footer(self, value): pass

    @property
    @parse_self_item_value()
    def webmod_page_block_debugs(self): return
    @webmod_page_block_debugs.setter
    @set_self_item_value_by_setter_with_agr(value_type='str')
    def webmod_page_block_debugs(self, value): pass

    @property
    @parse_self_item_value()
    def html_output_minimized(self): return
    @html_output_minimized.setter
    @set_self_item_value_by_setter_with_agr(value_type='bol')
    def html_output_minimized(self, value): pass

    @property
    @parse_self_item_value()
    def html_output_indentation(self): return
    @html_output_indentation.setter
    @set_self_item_value_by_setter_with_agr(value_type='str')
    def html_output_indentation(self, value): pass

    @property
    @parse_self_item_value()
    def html_output_comments(self): return
    @html_output_comments.setter
    @set_self_item_value_by_setter_with_agr(value_type='bol')
    def html_output_comments(self, value): pass

    @property
    @parse_self_item_value()
    def html_output_unspaced(self): return
    @html_output_unspaced.setter
    @set_self_item_value_by_setter_with_agr(value_type='bol')
    def html_output_unspaced(self, value): pass

    @property
    @parse_self_item_value()
    def html_title_delimiter(self): return
    @html_title_delimiter.setter
    @set_self_item_value_by_setter_with_agr(value_type='str')
    def html_title_delimiter(self, value): pass

    @property
    @parse_self_item_value()
    def html_title_ascending(self): return
    @html_title_ascending.setter
    @set_self_item_value_by_setter_with_agr(value_type='bol')
    def html_title_ascending(self, value): pass

    @property
    @parse_self_item_value()
    def url_root_path(self): return
    @url_root_path.setter
    @set_self_item_value_by_setter_with_agr(value_type='str')
    def url_root_path(self, value): pass

    @property
    @parse_self_item_value()
    def url_key_language(self): return
    @url_key_language.setter
    @set_self_item_value_by_setter_with_agr(value_type='str')
    def url_key_language(self, value): pass

    @property
    @parse_self_item_value()
    def url_key_mode(self): return
    @url_key_mode.setter
    @set_self_item_value_by_setter_with_agr(value_type='str')
    def url_key_mode(self, value): pass

    @property
    @parse_self_item_value()
    def url_key_module(self): return
    @url_key_module.setter
    @set_self_item_value_by_setter_with_agr(value_type='str')
    def url_key_module(self, value): pass

    @property
    @parse_self_item_value()
    def url_key_arguments(self): return
    @url_key_arguments.setter
    @set_self_item_value_by_setter_with_agr(value_type='str')
    def url_key_arguments(self, value): pass

    @property
    @parse_self_item_value()
    def url_key_keyword(self): return
    @url_key_keyword.setter
    @set_self_item_value_by_setter_with_agr(value_type='str')
    def url_key_keyword(self, value): pass

    @property
    @parse_self_item_value()
    def url_key_page(self): return
    @url_key_page.setter
    @set_self_item_value_by_setter_with_agr(value_type='str')
    def url_key_page(self, value): pass

    @property
    @parse_self_item_value()
    def url_key_orders(self): return
    @url_key_orders.setter
    @set_self_item_value_by_setter_with_agr(value_type='str')
    def url_key_orders(self, value): pass

    @property
    @parse_self_item_value()
    def url_key_filters(self): return
    @url_key_filters.setter
    @set_self_item_value_by_setter_with_agr(value_type='str')
    def url_key_filters(self, value): pass

    @property
    @parse_self_item_value()
    def url_key_items_per_page(self): return
    @url_key_items_per_page.setter
    @set_self_item_value_by_setter_with_agr(value_type='str')
    def url_key_items_per_page(self, value): pass

    @property
    @parse_self_item_value()
    def url_key_pages_per_group(self): return
    @url_key_pages_per_group.setter
    @set_self_item_value_by_setter_with_agr(value_type='str')
    def url_key_pages_per_group(self, value): pass

    @property
    @parse_self_item_value()
    def url_key_security(self): return
    @url_key_security.setter
    @set_self_item_value_by_setter_with_agr(value_type='str')
    def url_key_security(self, value): pass

    @property
    @parse_self_item_value()
    def url_key_reference(self): return
    @url_key_reference.setter
    @set_self_item_value_by_setter_with_agr(value_type='str')
    def url_key_reference(self, value): pass

    @property
    @parse_self_item_value()
    def pagination_items_per_page(self): return
    @pagination_items_per_page.setter
    @set_self_item_value_by_setter_with_agr(value_type='intp')
    def pagination_items_per_page(self, value): pass

    @property
    @parse_self_item_value()
    def pagination_pages_per_group(self): return
    @pagination_pages_per_group.setter
    @set_self_item_value_by_setter_with_agr(value_type='intp')
    def pagination_pages_per_group(self, value): pass

    @property
    @parse_self_item_value()
    def logo(self): return
    @logo.setter
    @set_self_item_value_by_setter_with_agr(value_type='str')
    def logo(self, value): pass
