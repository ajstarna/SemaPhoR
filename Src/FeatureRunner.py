''' this module will hold the base class GeneralFeatureRunner which can be extended to run the Featurizer on different sets, e.g. Gold sets, all dictionary pairs, etc
'''


import sys, time

from UniToASJPConverter import uniToASJP
from UniToALINEConverter import uniToALINE


import DefinitionCleaner


class FeatureRunner(object):

    def __init__(self, outputFeaturesFile, featurizer):
        self.outputFeaturesFile = outputFeaturesFile
        self.featurizer = featurizer

    # the enter and exit methods are definied to automatically open and close the output file                                                                                                              
    # these methods get called when executing a Python "with" statement 
    def __enter__(self):
        self.outputFeatureHandle = open(self.outputFeaturesFile, 'w')
        return self
        
    def __exit__(self, exc_type, exc_value, traceback):
        self.outputFeatureHandle.close()

    def writeFeaturesToFile(self):
        lineToPrint = self.featurizer.getOutputLine()
        self.outputFeatureHandle.write(lineToPrint + "\n")



class GeneralFeatureRunner(FeatureRunner):

    def __init__(self, outputFeaturesFile, featurizer):
        super().__init__(outputFeaturesFile, featurizer)
        self.asjpConversionDict = {}
        self.alineConversionDict = {}
        self.defnToCleanDict = {}


    def getASJP(self, uni):
        if uni in self.asjpConversionDict:
            asjp = self.asjpConversionDict[uni]
        else:
            asjp = uniToASJP(uni)
            self.asjpConversionDict[uni] = asjp
        return asjp


    def getALINE(self, uni):
        if uni in self.alineConversionDict:
            aline = self.alineConversionDict[uni]
        else:
            aline = uniToALINE(uni)
            self.alineConversionDict[uni] = aline
        return aline


    def getClean(self, defn):
        if defn in self.defnToCleanDict:
            clean = self.defnToCleanDict[defn]
        else:
            clean = DefinitionCleaner.cleanDef(defn)
            self.defnToCleanDict[defn] = clean
        return clean


    def featurizeGivenPair(self, word1, word2, asjp1, asjp2, aline1, aline2, def1, def2, cleanedDef1, cleanedDef2, acc1, acc2, classification=-1):
        ''' given a word pair in asjp and their definitions, runs the featurizer on them and outputs the pair
        and feature values to their respective files '''

        self.featurizer.setWords(word1, word2, asjp1, asjp2, aline1, aline2, def1, def2, cleanedDef1, cleanedDef2, acc1, acc2, classification)
        self.featurizer.runAllFeatures()
        self.writeFeaturesToFile()



        
class SubstringFeatureRunner(FeatureRunner):

    def __enter__(self):
        self.outputFeatureHandle = open(self.outputFeaturesFile, 'w')
        if (not self.trainingFlag) and self.featureDictFileName is not None:
            # we are testing, so need to read in feature dict from training
            #print("reading feature file")
            self.featurizer.readFeatureDictFromFile(self.featureDictFileName)
        return self
        
    def __exit__(self, exc_type, exc_value, traceback):
        self.outputFeatureHandle.close()
        if (self.trainingFlag) and self.featureDictFileName is not None:
            # if we are in training mode and have a given featureDict file name, then we write the features
            self.featurizer.writeFeatureDictToFile(self.featureDictFileName)


    def featurizeGivenPair(self, word1, word2, classification):
        self.featurizer.featurizeGivenPair(word1, word2, classification)
        self.writeFeaturesToFile()




