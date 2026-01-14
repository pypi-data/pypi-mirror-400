from .....functions.builtins import join_url
from .....functions.decorators import parse_self_x_item_value_or_set_by_func
from ....types.he import He


class Server(He):
    def __init__(self, system):
        super().__init__(system)

    @property
    def __websystem__(self): return self.__u__
    @property
    def __configs__(self): return self.__websystem__.configs
    def __deubg_warning__(self, content): raise RuntimeError('函数必须在继承类中重写')
    def __deubg_info__(self, content): raise RuntimeError('函数必须在继承类中重写')
    def make_response_text_html(self, code: str): raise RuntimeError('函数必须在继承类中重写')
    def make_response_text_plain(self, text: str): raise RuntimeError('函数必须在继承类中重写')
    def make_response_text_css(self, code: str): raise RuntimeError('函数必须在继承类中重写')
    def make_response_text_csv(self, code: str): raise RuntimeError('函数必须在继承类中重写')
    def make_response_text_markdown(self, code: str): raise RuntimeError('函数必须在继承类中重写')
    def make_response_text_xml(self, code: str): raise RuntimeError('函数必须在继承类中重写')
    # noinspection PyMethodMayBeStatic
    def make_response_error(self, title=None, heading=None, content=None):
        title = title or 'Error'
        heading = heading or 'Unknown Error Occurred'
        content = content or 'The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again.'
        return f'<!doctype html><html lang=en><title>{title}</title><h1>{heading}</h1><p>{content}</p>'

    def make_response_redirect(self, url): raise RuntimeError('函数必须在继承类中重写')
    def make_response_file(self, file, as_attachment=False, mimetype=None, download_name=None): raise RuntimeError('函数必须在继承类中重写')
    def make_response_404(self): raise RuntimeError('函数必须在继承类中重写')
    @property
    @parse_self_x_item_value_or_set_by_func()
    def root_url(self): return f'{self.__configs__.url_root_path.strip('/')}'
    def generate_url(self, *names): return join_url(self.root_url, *names)

    def run(self): raise RuntimeError('函数必须在继承类中重写')
