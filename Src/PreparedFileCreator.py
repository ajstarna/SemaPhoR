#!/usr/bin/env python3

import sys
import time

from UniToALINEConverter import uniToALINE

class ALINEFileCreator(object):
    def __init__(self, outputName):
        self.outputName = outputName
        self.uni2ALINEDict = {}

    def getALINE(self, uni):
        if uni in self.uni2ALINEDict:
            return self.uni2ALINEDict[uni]
        else:
            aline = uniToALINE(uni)
            self.uni2ALINEDict[uni] = aline
            return aline

    # the enter and exit methods are definied to automatically open and close the output file                                                                                                              
    # these methods get called when executing a Python "with" statement 
    def __enter__(self):
        self.outputFileHandle = open(self.outputName, 'w')
        return self
        
    def __exit__(self, exc_type, exc_value, traceback):
        self.outputFileHandle.close()

    def writeToFile(self, aline1, aline2):
        self.outputFileHandle.write(aline1 + " " + aline2 + "\n")
