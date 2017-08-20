#!/usr/bin/env python3

import sys
import time

from PreparedFileCreator import ALINEFileCreator

class ExamplesALINEFileCreator(ALINEFileCreator):
    def __init__ (self, examplePairsFile, outputName):
        super().__init__(outputName)
        self.examplePairsFile = examplePairsFile

    def createALINEFile(self):

        t1 = time.time()
        sys.stderr.write("\n")

        with open(self.examplePairsFile) as inputFile:
            length = sum(1 for line in inputFile)

        with open(self.examplePairsFile) as inputFile:
            for i, line in enumerate(inputFile):
                t2 = time.time()
                seconds = t2- t1
                minutes = seconds/60.0
                hours = minutes/60.0
                sys.stderr.write("\033[F")
                sys.stderr.write("{0} / {1}  pairs analyzed; Time so far is {2:.2f}s = {3:.2f}m = {4:.2f}h\n".format(i, length, seconds, minutes, hours))
                
                classification, wordString1, wordString2 = line.strip().split("\t\t")
                wordTuple1 = wordString1.split("\t")
                wordTuple2 = wordString2.split("\t")

                uni1 = wordTuple1[1]
                uni2 = wordTuple2[1]
                aline1 = self.getALINE(uni1)
                aline2 = self.getALINE(uni2)
                self.writeToFile(aline1, aline2)



if __name__ == "__main__":

    import optparse
    
    parser = optparse.OptionParser()
    parser.add_option('-o', action='store', dest='outputName', help="the output file.")
    parser.add_option('-i', action='store', dest='examplePairsFile', help="the input example pairs file.")

    options, args = parser.parse_args()


    if options.outputName is None:
        sys.stderr.write("Must provide the output name!\n")
        exit(-1)


    if options.examplePairsFile is None:
        sys.stderr.write("Must provide the input examples pairs file!\n")
        exit(-1)
        

    t1 = time.time()
    with ExamplesALINEFileCreator(options.examplePairsFile, options.outputName) as creator:
        creator.createALINEFile()
    t2 = time.time()
    seconds = t2- t1
    minutes = seconds/60.0
    hours = minutes/60.0
    sys.stderr.write("Time to run was {0:.2f}s = {1:.2f}m = {2:.2f}h\n".format(seconds, minutes, hours))



