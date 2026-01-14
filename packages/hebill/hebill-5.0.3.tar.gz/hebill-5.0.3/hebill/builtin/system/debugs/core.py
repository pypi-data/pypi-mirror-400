from ..components.debugs import Debugs as ModDebugs


class Debugs(ModDebugs):
    def __init__(self, s):
      super().__init__(s)
      self.configs.hook('prefix', s.configs, 'debug_prefix')
      self.configs.hook('printable', s.configs, 'debug_printable')
      self.configs.hook('saveable', s.configs, 'debug_saveable')
