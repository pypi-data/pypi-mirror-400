import os
from ..types.he.i import I as HI
from ...functions.decorators import parse_self_x_item_value_or_set_by_func


class I(HI):
    DIRNAM_DATA:str = '.data'
    DIRNAM_DATA_CONFIGS:str = 'configs'
    DIRNAM_DATA_SETTINGS:str = 'settings'
    DIRNAM_DATA_DATABASE_TABLES:str = 'database_tables'
    DIRNAM_DATA_DATABASE_DATA:str = 'database_data'
    DIRNAM_DATA_MULTILINGALS:str = 'multilinguals'
    DIRNAM_LOGS:str = '.logs'
    DIRNAM_PUBLIC:str = '.public'

    FILNAM_CONFIGS:str = 'configs.json'
    FILNAM_SETTINGS:str = 'settings.json'

    MLKEY_NAME:str = 'NAME'
    MLKEY_ABBR:str = 'ABBR'
    MLKEY_TITLE:str = 'TITLE'
    MLKEY_DESC:str = 'DESP'
    MLKEY_LINK_TITLE:str = 'LINK_TITLE'
    MLKEY_PAGE_TITLE:str = 'PAGE_TITLE'
    MLKEY_BDCD_TITLE:str = 'BDCD_TITLE'

    LAN_CN = 'cn'
    LAN_GB = 'gb'
    LANS: list[str] = [LAN_CN, LAN_GB]
    WEBMOD_CDN = 'cdn'
    WEBMOD_PUB = 'pub'
    WEBMOD_AJX = 'ajax'
    WEBMOD_FIL = 'file'
    WEBMOD_LAY = 'layout'
    WEBMOD_JSN = 'json'
    WEBMOD_PAG = 'page'
    WEBMOD_STM = 'steam'
    WEBMODS: list[str] = [WEBMOD_CDN, WEBMOD_PUB, WEBMOD_AJX, WEBMOD_FIL, WEBMOD_LAY, WEBMOD_JSN, WEBMOD_PAG, WEBMOD_STM]
    DATCOL_BIN = 'bigint'
    DATCOL_CHA = 'char'
    DATCOL_DOB = 'double'
    DATCOL_FLT = 'float'
    DATCOL_INT = 'int'
    DATCOL_TXT = 'text'
    DATCOL_TIN = 'tinyint'
    DATCOL_VCH = 'varchar'
    DATCOLS: list[str] = [DATCOL_BIN, DATCOL_CHA, DATCOL_DOB, DATCOL_FLT, DATCOL_INT, DATCOL_TXT, DATCOL_TIN, DATCOL_VCH]

    @property
    def builtin_folder(self): return self.folder.parent
    @property
    @parse_self_x_item_value_or_set_by_func()
    def builtin_mod_path(self): return self.mod_path.rel_mod_path('.')
    @property
    def builtin_mod_type(self): return self.builtin_mod_path.mod_type
    @property
    def hebill_folder(self): return self.builtin_folder.parent
    @property
    @parse_self_x_item_value_or_set_by_func()
    def hebill_mod_path(self): return self.builtin_mod_path.rel_mod_path('.')
    @property
    def hebill_mod_type(self): return self.hebill_mod_path.mod_type
    @property
    def project_folder(self): return self.hebill_folder.parent
    @property
    @parse_self_x_item_value_or_set_by_func()
    def project_mod_path(self): return self.hebill_mod_path.rel_mod_path('.')
    @property
    def project_mod_type(self): return self.project_mod_path.mod_type
    @property
    @parse_self_x_item_value_or_set_by_func()
    def cdn_folder(self): return self.hebill_folder.child_folder('cdn')
    @property
    @parse_self_x_item_value_or_set_by_func()
    def website_folder(self): return self.hebill_folder.child_folder('website')
    @property
    @parse_self_x_item_value_or_set_by_func()
    def website_mod_path(self): return self.hebill_mod_path.rel_mod_path('.website')
    @property
    def website_mod_type(self): return self.hebill_folder.child_folder('website')

    @parse_self_x_item_value_or_set_by_func()
    def is_pip_installed(self): return 'site-packages' in self.folder

    @property
    @parse_self_x_item_value_or_set_by_func()
    def working_folder(self): return self.__he__.components.folder(os.getcwd())
