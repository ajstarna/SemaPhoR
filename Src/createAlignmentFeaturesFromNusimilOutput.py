#!/usr/bin/env python3

''' this file reads the prepared ALINE pairs file along with the output nusimil file and writes the nusimil score and consonant score to binary file
after associating the pairs with the nusimil outputs.


example run:
./createAlignmentFeaturesFromNusimilOutput.py -p preparedALINEFileCreeFox.txt -n nusimilOutputCreeFox.txt -t 0.35 -o alignmentFeaturesCreeFox0.35Threshold.bin

'''

import sys
import time

from alignmentFeatures import AlignmentFeatureValuesWriter

class AlignmentFeatureValuesWriterFromNusimil(AlignmentFeatureValuesWriter):
    # class to read the aline pairs file and the nusimil output file, associate them together, and to write the nusimil and consanant score to binary file


    def __init__ (self, alineFileName, nusimilFileName, outputFileName, threshold):
        super().__init__(outputFileName)
        self.alineFileName = alineFileName
        self.nusimilFileName = nusimilFileName
        self.threshold = threshold


    def createFeatures(self):
        # goes through line by line in the files and writes the current values to the output file
        numLines = 0
        with open(self.alineFileName) as file:
            for line in file:
                numLines += 1

        sys.stderr.write("\n\n")

        with open(self.alineFileName) as alineFile:
            with open(self.nusimilFileName) as nusimilFile:
                currentLines = []
                numChunks = 0
                for line in nusimilFile:
                    line = line.strip()
                    if line == "":
                        # empty lines signify the end of a current pair output, so write it to file
                        numChunks += 1
                        sys.stderr.write("\033[F")
                        sys.stderr.write("{0} / {1} nusimil chunks analyzed\n".format(numChunks, numLines))
                        
                        aLine = alineFile.readline()
                        score, normalizedAlignedCons = self.getAlignmentFeaturesFromNusimilOutput(currentLines)
                        currentLines = []
                        if score > self.threshold:
                            # only want to write to file those pairs that pass the threshold
                            aLine = aLine.strip('\n')
                            aline1, aline2 = aLine.split()
                            self.writeToBinaryFile(aline1, aline2, score, normalizedAlignedCons)

                    else:
                        currentLines.append(line)


    

if __name__ == "__main__":

    import optparse
    
    parser = optparse.OptionParser()
    parser.add_option('-o', action='store', dest='outputName', help="the output file.")
    parser.add_option('-n', action='store', dest='nusimilFile', help="the nusimil output file.")
    parser.add_option('-p', action='store', dest='alinePairs', help="the aline pairs file.")
    parser.add_option('-t', action='store', dest='threshold', help="the threshold score required to write a pair to the file. By setting this threshold, the final file will be a lot smaller.",
                      default=-1) # a default of -1 means all pairs will pass the threshold and be written

    options, args = parser.parse_args()


    if options.outputName is None:
        sys.stderr.write("Must provide the output name!\n")
        exit(-1)
        

    if options.nusimilFile is None:
        sys.stderr.write("Must provide the nusimil output file!\n")
        exit(-1)


    if options.alinePairs is None:
        sys.stderr.write("Must provide the aline words file!\n")
        exit(-1)

    threshold = float(options.threshold)

    t1 = time.time()
    with AlignmentFeatureValuesWriterFromNusimil(options.alinePairs, options.nusimilFile, options.outputName, threshold) as creator:
        creator.createFeatures()


    t2 = time.time()
    seconds = t2- t1
    minutes = seconds/60.0
    hours = minutes/60.0
    sys.stderr.write("Time to run was {0:.2f}s = {1:.2f}m = {2:.2f}h\n".format(seconds, minutes, hours))

