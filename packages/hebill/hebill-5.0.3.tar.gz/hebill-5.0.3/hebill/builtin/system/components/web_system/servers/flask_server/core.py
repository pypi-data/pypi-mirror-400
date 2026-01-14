import logging
import os
import uuid
from flask import Flask, request, Response, abort, redirect, session, send_file
from ...server import Server


class FlaskServer(Server):
    # 运行start后怎么实现子线程运行，不影响主线程继续运行
    def __deubg_warning__(self, content=None, error=None, comment=None, file=None): self.__s__.debugs.output.warning(content, error, comment, file, [self.__configs__.module, f'{self.__configs__['host']}:{self.__configs__['port']}', request.remote_addr])
    def __deubg_info__(self, content=None, error=None, comment=None, file=None): self.__s__.debugs.output.info(content, error, comment, file, [self.__configs__.module, f'{self.__configs__['host']}:{self.__configs__['port']}', request.remote_addr])
    def make_response_text_html(self, code: str): return Response(code, mimetype='text/html')
    def make_response_text_plain(self, text: str): return Response(text, mimetype='text/html')
    def make_response_text_css(self, code: str): return Response(code, mimetype='text/html')
    def make_response_text_csv(self, code: str): return Response(code, mimetype='text/html')
    def make_response_text_markdown(self, code: str): return Response(code, mimetype='text/html')
    def make_response_text_xml(self, code: str): return Response(code, mimetype='text/html')

    def make_response_redirect(self, url): return redirect(url)
    def make_response_file(self, file, as_attachment=False, mimetype=None, download_name=None):
        msg = f'请求文件[GET]: {file} <=> {request.url}'
        if os.path.isfile(file):
            self.__deubg_info__(msg)
            return send_file(file, as_attachment=as_attachment, mimetype=mimetype, download_name=download_name)
        self.__deubg_warning__(msg)
        return self.make_response_404()
    def make_response_404(self): return abort(404)

    def run(self):
        logging.getLogger('werkzeug').setLevel(logging.ERROR)
        app = Flask(__name__)
        app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 86400
        app.secret_key = uuid.uuid4().hex
        @app.route('/', defaults={'path': ''}, methods=['GET', 'POST'])
        @app.route('/<path:path>', methods=['GET', 'POST'])
        def home(path):
            if not 'hebill' in session: session['hebill'] = {}
            if not 'id' in session: session['hebill']['id'] = str(uuid.uuid4())
            client = self.__websystem__.clients.get(session['hebill']['id'])
            client.hook_session(session['hebill'])
            client.request.headers.update({
                'host': request.headers.get('Host'),
                'connection': request.headers.get('Connection'),
                'cache_control': request.headers.get('Cache-Control'),
                'sec_ch_ua': request.headers.get('Sec-Ch-Ua'),
                'sec_ch_ua_mobile': request.headers.get('Sec-Ch-Ua-Mobile'),
                'sec_ch_ua_platform': request.headers.get('Sec-Ch-Ua-Platform'),
                'upgrade_insecure_requests': request.headers.get('Upgrade-Insecure-Requests'),
                'user_agent': request.headers.get('User-Agent'),
                'accept': request.headers.get('Accept'),
                'sec_fetch_site': request.headers.get('Sec-Fetch-Site'),
                'sec_fetch_mode': request.headers.get('Sec-Fetch-Mode'),
                'sec_fetch_user': request.headers.get('Sec-Fetch-User'),
                'sec_fetch_dest': request.headers.get('Sec-Fetch-Dest'),
                'accept_encoding': request.headers.get('Accept-Encoding'),
                'accept_language': request.headers.get('Accept-Language'),
                'cookie': request.headers.get('Cookie'),
            })
            client.request.form.update(request.form.to_dict())
            client.request.update({
                'method': request.method,
                'url': request.url,
                'path': request.path,
                'remote_addr': request.remote_addr,
            })
            # return 'Hello World'
            from ...website import Website
            return Website(self.__websystem__, client).response()

        self.__s__.debugs.output.info(f'网站开始运行：http://{'127.0.0.1' if self.__configs__['host'] == '0.0.0.0' else self.__configs__['host']}:{self.__configs__['port']}')
        app.run(host=self.__configs__['host'], port=self.__configs__['port'], debug=False, threaded=False)
