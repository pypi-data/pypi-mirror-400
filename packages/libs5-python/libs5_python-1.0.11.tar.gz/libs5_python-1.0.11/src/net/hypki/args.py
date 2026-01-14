'''
Created on 15-06-2013

@author: ahypki
'''

import sys

class ArgUtils:
    
    def getStrings(name):  # @NoSelf
        v = []
        for i in range(len(sys.argv)):
            if sys.argv[i] == "--" + name or sys.argv[i] == "-" + name:
                v.append(sys.argv[i + 1].strip())
        return v

    def getString(name, defaultvalue):  # @NoSelf
        for i in range(len(sys.argv)):
            if sys.argv[i] == "--" + name or sys.argv[i] == "-" + name:
                return sys.argv[i + 1].strip() if i + 1 < len(sys.argv) else defaultvalue
        return defaultvalue
    
    def isArgPresent(name):  # @NoSelf
        for i in range(len(sys.argv)):
            if sys.argv[i] == "--" + name or sys.argv[i] == "-" + name:
                return True
        return False
    
    def getArgsCount():  # @NoSelf
        return len(sys.argv)
    
    def getArg(idx):  # @NoSelf
        return sys.argv[idx]