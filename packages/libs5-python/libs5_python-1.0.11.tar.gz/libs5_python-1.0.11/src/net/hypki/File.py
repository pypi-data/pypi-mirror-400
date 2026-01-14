'''
Created on Oct 14, 2025

@author: ahypki
'''
import os
import shutil
from net.hypki.io import append_to_file

class File(object):
    '''
    classdocs
    '''
    __absPath = None

    def __init__(self, path):
        '''
        Constructor
        '''
        if isinstance(path, str):
            self.setAbsPath(path)
        elif len(path) == 1:
            self.setAbsPath(path[0])
        else:
            self.setAbsPath("/".join(path))
            # p2 = "/"
            # for p1 in path:
            #     p1 += 
        
    def getAbsPath(self):
        return self.__absPath


    def setAbsPath(self, path):
        if "~" in path:
            home_directory = os.path.expanduser("~")
            path = path.replace("~", home_directory + "/")
        # self.__absPath = PosixPath(path).expanduser()
        self.__absPath = os.path.abspath(path)
        
    def exists(self):
        return os.path.exists(self.__absPath)
    
    def mkdirs(self):
        os.makedirs(self.__absPath, exist_ok=True)

    
    def copy(self, destination):
        shutil.copy2(self.__absPath, destination)

    def mv(self, destination):
        shutil.move(self.__absPath, destination)
    
    def remove(self):
        os.remove(self.__absPath)
    
    def append(self, line):
        append_to_file(self.getAbsPath(), line)
    
