'''
Created on Oct 14, 2025

@author: ahypki
'''

class StringUtils(object):
    '''
    classdocs
    '''


    def __init__(self, params):
        '''
        Constructor
        '''
        pass
    
    def notEmpty(s):  # @NoSelf
        return not StringUtils.isEmpty(s) #len(s.strip()) > 0 if s is not None else False 
    
    def isEmpty(s):  # @NoSelf
        return s is None or len(s.strip()) == 0 if s is not None else False 