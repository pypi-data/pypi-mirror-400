import os, platform
class Utils:
    @staticmethod
    def maxlen(data):
        out = []
        for i in data:
            out.append(len(str(i)))
        return max(out)
    @staticmethod
    def cls():
        if platform.system() == 'Windows':
            os.system('cls')
        else:
            os.system('clear')

class color:
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'

    RESET = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    @staticmethod
    def set(text, *col):
        data = col if isinstance(col, list) else [col]
        if isinstance(col, tuple):
            nd = []
            for i in col: nd.append(i)
            data = nd
        return f"{' '.join(data)}{text}{color.RESET}"