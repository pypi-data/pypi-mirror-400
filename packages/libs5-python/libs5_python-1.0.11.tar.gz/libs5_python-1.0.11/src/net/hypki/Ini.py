'''
Created on Oct 15, 2025

@author: ahypki
'''
import re

class Ini(object):
    '''
    classdocs
    '''
    __path = None
    __iniLines = None

    def __init__(self, path):
        '''
        Constructor
        '''
        self.__path = path
        
    def __getIni(self):
        if self.__iniLines is None:
            self.__iniLines = open(self.__path, "r").readlines()
                
        return self.__iniLines
    
    def __isKey(self, line):
        k = self.__getKey(line)
        return False if k is None else True
    
    def __getKey(self, line):
        m = re.match("^[\s]*(\w[\w\d]*)[\s]*=[\s]*.*$", line)
        if m:
            return m.group(1)
        return None
    
    def __isSection(self, line):
        sec = self.__getSection(line)
        return False if sec is None else True
    
    def __getSection(self, line):
        m = re.match("^[\s]*\[(\w[\w\d]+)\][\s]*$", line)
        if m:
            return m.group(1)
        return None
        
    def getSections(self):
        sections = []
        for line in self.__getIni():
            if self.__isSection(line):
                sections.append(self.__getSection(line))
        return sections
    
    def getKeys(self, section):
        keys = []
        currentSection = None
        for line in self.__getIni():
            if self.__isSection(line):
                currentSection = self.__getSection(line)
                continue
            if self.__isKey(line):
                if currentSection is not None and currentSection == section:
                    keys.append(self.__getKey(line))
        return keys
    
    def remove(self, section, key):
        v = self.get(section, key)
        if v is None:
            return
        
        newLines = []
        currentSection = None
        for line in self.__getIni():
            if self.__isSection(line):
                currentSection = self.__getSection(line)
            
            currentKey = None
            if self.__isKey(line):
                currentKey = self.__getKey(line)
                
            if currentSection is not None and currentSection == section and currentKey is not None and currentKey == key:
                # not adding this line
                pass
            else:
                newLines.append(line)
                
        self.__iniLines = newLines
    
    def add(self, section, key, value):
        v = self.get(section, key)
        forceAdd = True
        if v is not None:
            forceAdd = False
        self.set(section, key, value, forceAdd=forceAdd)
    
    def set(self, section, key, value, forceAdd = False):
        newLines = []
        currentSection = None
        newKeyAdded = False
        for line in self.__getIni():
            lineAdded = False
            
            if self.__isSection(line):
                currentSection = self.__getSection(line)
                
            if newKeyAdded is False and forceAdd and currentSection is not None and currentSection == section:
                newLines.append(line)
                newLines.append(key + " = " + value)
                lineAdded = True
                newKeyAdded = True
            else:
                if self.__isKey(line):
                    currentKey = self.__getKey(line)
                    if currentSection is not None and currentSection == section and currentKey == key:
                        newLines.append(key + " = " + value)
                        lineAdded = True
                        newKeyAdded = True
                    
            if not lineAdded:
                newLines.append(line)
                
        if newKeyAdded is False:
            if forceAdd:
                newLines.append(f"")
                newLines.append(f"[{section}]")
                newLines.append(f"{key} = {value}")
                
        self.__iniLines = newLines
        
    def getFloat(self, section, key, defaultValue = 0.0):
        g = self.get(section, key, defaultValue = None)
        if g is None:
            return defaultValue
        elif isinstance(g, str):
            return float(g)
        else:
            return defaultValue
        
    def getInt(self, section, key, defaultValue = 0):
        g = self.get(section, key, defaultValue = None)
        if g is None:
            return defaultValue
        elif isinstance(g, str):
            return int(g)
        elif isinstance(g, int):
            return g
        else:
            return defaultValue
        
    def get(self, section, key, defaultValue = None):
        currentSection = None
        for line in self.__getIni():
            if self.__isSection(line):
                currentSection = self.__getSection(line)
                continue
            if self.__isKey(line):
                currentKey = self.__getKey(line)
                if currentSection is not None and currentSection == section and currentKey == key:
                    return line[(line.index("=") + 1):].strip()
        return defaultValue

    # names: this is list of strings in a format section.key e.g.: ['Mcluster.n', 'Mcluster.rh_mcl']
    # values: tuple with values e.g.: ('50000', '1.0')
    def updateValues(self, names, values):
        i = 0
        for oneCarth in values:
            sec = names[i].split(".")[0]
            key = names[i].split(".")[1]
            value = oneCarth
        
            self.set(sec, key, value)
            i += 1
        
    def save(self, newPath = None):
        if self.__iniLines is not None:
            with open(self.__path if newPath is None else newPath, 'w') as f:
                for line in self.__iniLines:
                    f.write(f"{line.strip()}\n")
