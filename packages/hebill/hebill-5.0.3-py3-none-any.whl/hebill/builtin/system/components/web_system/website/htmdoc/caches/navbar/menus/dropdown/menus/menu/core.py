class Menu(dict):
    def __init__(self, title=None, url=None):
        super().__init__()
        self.title = title
        self.url = url

    @property
    def title(self): return self.get('title')
    @title.setter
    def title(self, value): self['title'] = value

    @property
    def url(self): return self.get('url')
    @url.setter
    def url(self, value): self['url'] = value
