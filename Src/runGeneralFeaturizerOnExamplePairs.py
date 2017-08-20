#!/usr/bin/env python3

''' this file reads the example pairs file which was already created, and featurizes all pairs from this file. 
It outputs the feature values in a given output file
'''


import sys
import time
import random

from FeatureRunner import GeneralFeatureRunner
from GeneralFeaturizer import GeneralFeaturizer

class RunnerForExamples(GeneralFeatureRunner):
    def __init__(self, examplePairsFile, outputFeaturesFile, featurizer):
        super().__init__(outputFeaturesFile, featurizer)
        self.numPositiveExamples = 0
        self.numNegativeExamples = 0
        self.examplePairsFile = examplePairsFile



    def getInputFileLength(self):
        with open(self.examplePairsFile) as inputFile:
            self.length = sum(1 for line in inputFile)

    def run(self):
        self.getInputFileLength()

        sys.stderr.write("\n\n")
        with open(self.examplePairsFile) as inputFile:
            for i, line in enumerate(inputFile):
                sys.stderr.write("\033[F")
                sys.stderr.write("pair {0} / {1}\n".format(i, self.length))
                
                classification, wordString1, wordString2 = line.strip().split("\t\t")
                wordTuple1 = wordString1.split("\t")
                wordTuple2 = wordString2.split("\t")
                
                acc1, uni1, def1 = wordTuple1
                acc2, uni2, def2 = wordTuple2
                
                asjp1 = self.getASJP(uni1)
                aline1 = self.getALINE(uni1)
                asjp2 = self.getASJP(uni2)
                aline2 = self.getALINE(uni2)

                cleanedDef1 = self.getClean(def1)
                cleanedDef2 = self.getClean(def2)

                # map the classification symbol to the value that SVM_light expects
                if classification == "+":
                    classification = 1
                else:
                    classification = -1

                self.featurizeGivenPair(uni1, uni2, asjp1, asjp2, aline1, aline2, def1, def2, cleanedDef1, cleanedDef2, acc1, acc2, classification)




if __name__ == "__main__":

    import optparse
    
    parser = optparse.OptionParser()
    parser.add_option('-i', action='store', dest='inputPairsName', help="the input name for pairs, i.e. the pairs to featurize.")
    parser.add_option('-f', action='store', dest='outputFeaturesName', help="the output name for features. default = 'training_feature_values_cree_meno.txt'")
    parser.add_option('-a', action='store', dest='alignmentFeaturesFile', help="the alignment feature file.", default=None)
    parser.add_option('--lang', '-l', action='store', dest='defnLanguage', help="the language of the definitions in the example pairs. default = en", default="en")
    
    # to turn off specific feature(s)
    parser.add_option('-u', action='store', dest='UseFeatureNumbers', help="feature numbers to use. ex: 1,2,9,13")
    parser.add_option('-y', action='store', dest='UseFeatureType', help="feature type to use. ex: 'surface' or 'word2Vec'")

                      
    options, args = parser.parse_args()

    if options.inputPairsName is None:
        sys.stderr.write("Must provide input file!\n")
        exit(-1)
                      
    if options.UseFeatureNumbers is not None:
        stringNumbers =  options.doNotUseFeatureNumbers.split(",")
        try:
            featureNumbersToUse = [int(num) for num in stringNumbers]
        except:
            sys.stderr.write("Invalid feature numbers provided as argument!\n")
            exit(-1)
    elif options.UseFeatureType is not None:
        featureNumbersToUse = options.UseFeatureType
    else:
        # if no feature numbers specified, then use a default featurizer
        featureNumbersToUse = GeneralFeaturizer.allFeatures

    featurizer = GeneralFeaturizer(options.defnLanguage, options.alignmentFeaturesFile, featureNumbersToUse)
    # now we have our featurizer created
    t1 = time.clock()
    with RunnerForExamples(options.inputPairsName, options.outputFeaturesName, featurizer) as runner:
        runner.run()
    t2 = time.clock()
    seconds = t2- t1
    minutes = seconds/60.0
    hours = minutes/60.0
    sys.stderr.write("Time to run was {0:.2f}s = {1:.2f}m = {2:.2f}h\n".format(seconds, minutes, hours))


