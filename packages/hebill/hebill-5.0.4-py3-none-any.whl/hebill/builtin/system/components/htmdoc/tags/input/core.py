from ...nodes.tag import Tag


class Input(Tag):
    __hd_tag_pairable__ = False
    def __init__(self, u, name: str = None, value: str = None, attributes:dict[str, str|int|float|None]=None):
        if isinstance(attributes, dict):
            if 'type' not in attributes:
                attributes['type'] = 'text'
        else:
            attributes = {'type': 'text'}
        if name is not None: attributes['name'] = name
        if value is not None: attributes['value'] = value
        Tag.__init__(self, u, None, attributes)
