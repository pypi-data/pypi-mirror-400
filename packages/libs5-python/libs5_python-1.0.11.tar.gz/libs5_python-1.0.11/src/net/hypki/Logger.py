'''
Created on Aug 13, 2025

@author: ahypki
'''
from rich.console import Console

console = Console()

class Logger:
    BLUE = '[blue]'#'\033[94m'
    BLUE_END = '[/blue]'
    GREEN = '[green]'#'\033[92m'
    GREEN_END = '[/green]'
    RED = '[red]'#'\033[91m'
    RED_END = '[/red]'
    WARNING = '[yellow]'#'\033[93m'
    WARNING_END = '[/yellow]'
    FAIL = RED#'\033[91m'
    FAIL_END = RED_END
    # ENDC = '\033[0m'
    
    DEBUG = False
    INFO = True
    
    PRINT_LEVEL = True
    
    # def blue(s):  # @NoSelf
    #     return Logger.BLUE + s + Logger.BLUE_END
    
    def debug(msg, printLogLevel = True, printNewLine = True):  # @NoSelf
        if Logger.DEBUG:
            print(("DEBUG " if printLogLevel and Logger.PRINT_LEVEL else '') 
                  + str(msg), 
#                  no_wrap = True,
                  end = ('\n' if printNewLine else ''))
    
    def info(msg, printLogLevel = True, printNewLine = True):  # @NoSelf
        if Logger.INFO:
            print(("INFO  " if printLogLevel and Logger.PRINT_LEVEL else '') 
                  + str(msg), 
#                  no_wrap = False,
#                  crop = False,
#                  width = 1280,
                  end = ('\n' if printNewLine else ''))
        
    def warn(msg, printLogLevel = True, printNewLine = True):  # @NoSelf
        print(("WARN  " if printLogLevel and Logger.PRINT_LEVEL else '') 
              + str(Logger.WARNING + msg + Logger.WARNING_END),
#              no_wrap = True, 
              end = ('\n' if printNewLine else ''))
    
    def error(msg, printLogLevel = True, printNewLine = True):  # @NoSelf
        print(("ERROR " if printLogLevel and Logger.PRINT_LEVEL else '') 
              + str(msg), 
#              no_wrap = True,
              end = ('\n' if printNewLine else ''))
