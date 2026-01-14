from ...nodes.tag import Tag


class Img(Tag):
    __hd_tag_pairable__ = False
    def __init__(self, u, url=None, width=None, height=None, title:str= None, attributes:dict[str, str|int|float|None]=None):
        super().__init__(u, "img", attributes)
        if url: self.attributes['src'] = url
        if width: self.attributes['width'] = width
        if height: self.attributes['height'] = height
        if title: self.attributes['alt'] = title

