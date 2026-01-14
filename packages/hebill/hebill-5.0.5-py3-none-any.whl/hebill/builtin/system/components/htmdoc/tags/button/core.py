from ...nodes.tag import Tag


class Button(Tag):
    def __init__(self, u, title=None, attributes:dict[str, str|int|float|None]=None):
        if isinstance(attributes, dict):
            if 'type' not in attributes:
                attributes['type'] = 'button'
        else: attributes = {'type':'button'}
        Tag.__init__(self, u, None, title, attributes)
