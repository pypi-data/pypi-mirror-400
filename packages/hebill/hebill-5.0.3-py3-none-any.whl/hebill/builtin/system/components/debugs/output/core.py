from ....types.he import He
from colorama import Fore, Style


class Output(He):
    def print(self, content=None, error=None, comment=None, file=None, prefix=None, color=None, bgcolor=None, bright=None):
        text = Fore.BLUE + self.__u__.make_prefix(prefix)
        if bgcolor: text += bgcolor
        if color: text += color
        if bright: text += Style.BRIGHT
        text += str(content)
        if error: text += f'{Fore.RED + Style.DIM} # {error}'
        if comment: text += f'{Fore.WHITE + Style.DIM} #{comment}'
        if file: text += f'{Fore.WHITE + Style.DIM} #File:"{file}",'
        text += Style.RESET_ALL
        return print(text)

    def primary(self, content=None, error=None, comment=None, file=None, prefix=None): return self.print(content, error, comment, file, prefix, '\033[38;2;200;200;200m')
    def secondary(self, content=None, error=None, comment=None, file=None, prefix=None): return self.print(content, error, comment, file, prefix, Fore.BLUE)
    def success(self, content=None, error=None, comment=None, file=None, prefix=None): return self.print(content, error, comment, file, prefix, Fore.GREEN)
    def warning(self, content=None, error=None, comment=None, file=None, prefix=None): return self.print(content, error, comment, file, prefix, Fore.YELLOW)
    def danger(self, content=None, error=None, comment=None, file=None, prefix=None): return self.print(content, error, comment, file, prefix, Fore.RED)
    def info(self, content=None, error=None, comment=None, file=None, prefix=None): return self.print(content, error, comment, file, prefix, Fore.CYAN)
    def comment(self, content=None, error=None, comment=None, file=None, prefix=None): return self.print(content, error, comment, file, prefix, Fore.WHITE)
