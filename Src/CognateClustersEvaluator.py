#!/usr/bin/env python3

from collections import defaultdict

from GoldEvaluator import GoldEvaluator
import metrics

from LanguageDictParser import AlgonquianLanguageDictParser




import DefinitionCleaner


from DefSetsReader import DefSetsReader

class ClusterCreatorFromLangDicts(object):
    def __init__(self, smallDataSets, cognateFileToEvaluate):
        self.smallDataSets = smallDataSets
        self.allTuples = set() # keep track of all word tuples        
        self.cognateFileToEvaluate = cognateFileToEvaluate
        self.setUpClustering()


    def parseLanguageFiles(self):
        ''' reads the language dictionaries and adds each cleaned word tuple to a set of all tuples, used to keep track of
        which are put into a cluster or not.
        '''
        if self.smallDataSets:
            ldp = AlgonquianLanguageDictParserSmall()
        else:
            ldp = AlgonquianLanguageDictParser()
        self.langDicts = ldp.parseAllFiles()

        for langAcc in ldp.langs:
            langDict = self.langDicts[langAcc]
            for word in langDict:
                definitions = langDict[word]
                self.currentUniWord = word
                for defn in definitions:
                    cleanedDef = DefinitionCleaner.cleanDef(defn)
                    wordTuple = (langAcc, word, cleanedDef)
                    self.allTuples.add(wordTuple) 



    def setUpClustering(self):
        '''this method creates the cluster of all lang dict words in the format that metrics.py expects. 
        i.e. a dictionary mapping from arbitrary cluster labels to lists of word tuples in the cluster.
        all words not part of any group are in their own cluster.
        '''
        self.clusterID = 0
        self.clusterDict = defaultdict(list) # maps a number to a corresponding cluster

        self.parseLanguageFiles()
        self.parseOutputFile() # this method must be created in inherited classes
        print("number of proto set clusters = {0}".format(len(self.clusterDict)))
        self.clusterRemainingTuples()


    def addToClusterDict(self, words):
        for word in words:
            langAcc, word, defn  = word[:3] # the first three parts are (acc, word, defn)
            cleanedDef = DefinitionCleaner.cleanDef(defn)
            wordTuple = (langAcc, word, cleanedDef)
            if wordTuple in self.allTuples:
                self.allTuples.remove(wordTuple) 
            self.clusterDict[self.clusterID].append(wordTuple)
            #print("appending tuple {0}".format(wordTuple))


    def clusterRemainingTuples(self):
        ''' the tuples still remaining in self.allTuples need to be placed into their own cluster '''
        print("Number of single word clusters = {0}\n".format(len(self.allTuples)))
        for wordTuple in self.allTuples:
            self.clusterDict[self.clusterID].append(wordTuple)
            self.clusterID += 1


    def printOutClusterings(self):
        print("single word clusters")
        for clusterLabel in self.clusterDict:
            cluster = self.clusterDict[clusterLabel]
            if len(cluster) == 1:
                print(cluster[0])

        print("\n\n\nmulti word clusters")
        for clusterLabel in self.clusterDict:
            cluster = self.clusterDict[clusterLabel]
            if len(cluster) > 1:
                print(cluster)



class DefSetClusterCreator(ClusterCreatorFromLangDicts):

    def parseOutputFile(self):
        ''' reads the outputted clusters and puts the words in each set into the same cluster
        as these are put into a cluster, they are removed from the self.allTuples set. '''
        defSetsReader = DefSetsReader()
        defSetsReader.readFile(self.cognateFileToEvaluate)
        for defSet in defSetsReader:
            self.addToClusterDict(defSet.wordTupleList)
            self.clusterID += 1


class PutTogetherClusterCreator(ClusterCreatorFromLangDicts):
    # this class takes the output sets and puts them into one big set
    # this class gives an idea of how many of the total cognate words were put into a set

    def parseOutputFile(self):
        # reads the system output sets file and put all primary and secondary words from each set and 
        #places them all into one cluster. 
        #as these are put into a cluster, they are removed from the self.allTuples set. 
        outputParser = OutputParser()
        outputSets = outputParser.getProtoSets(self.cognateFileToEvaluate)
        for outputSet in outputSets:
            primaries, secondaries = outputParser.getPrimariesAndSecondaries(outputSet)
            self.addToClusterDict(primaries)
            self.addToClusterDict(secondaries)



class MaxRecallClusterCreator(ClusterCreatorFromLangDicts):
    def parseOutputFile(self):
        # there is no output file.
        # theoretically we could create a Def or System output file which places all words into the same set,
        # but this is unneccessary. Instead, we just place all words from the lang dicts into the same set within this
        # ClusterCreator
        return

    def clusterRemainingTuples(self):
        ''' the tuples still remaining in self.allTuples need to be placed into the SAME cluster '''
        for wordTuple in self.allTuples:
            self.clusterDict[self.clusterID].append(wordTuple)

class MaxPrecisionClusterCreator(ClusterCreatorFromLangDicts):
    def parseOutputFile(self):
        # there is no output file.
        # theoretically we could create a Def or System output file which places all words into their own set,
        # but this is unneccessary. ClusterRemainingTuples() will automatically place all the words into their own set
        # since there is no output file
        return

    def clusterRemainingTuples(self):
        ''' the tuples still remaining in self.allTuples need to be placed into their own cluster,
        EXCEPT for the first two. we do this just so the metrics do not have a divide by 0 error'''
        first = True
        for wordTuple in self.allTuples:
            self.clusterDict[self.clusterID].append(wordTuple)
            if first:
                # don't increase the cluster id the first time
                first = False
                continue
            self.clusterID += 1



class CognateClustersEvaluator(object):

    def __init__(self, goldSetsFile, clusters):
        self.goldEvaluator = GoldEvaluator(goldSetsFile)
        self.clusterDict = clusters


    def runAllEvaluationMetrics(self):
        self.evaluateBcubed(False)
        self.evaluateBcubed(True)
        self.evaluateMUC()
        self.evaluatePairWise()
        self.evaluatePurity()


    def evaluateBcubed(self, zeroWeightSingletons):
        ''' main method which sets up the clusters by reading in files and passes the clusters to the bCubed algorithm '''

        if zeroWeightSingletons:
            print("Zero-weight singletons.")
        else:
            print("Do not zero-weight singletons")

        print("Calculating bCubed...")
        recall, precision, fscore = metrics.bCubed(self.clusterDict, self.goldEvaluator, zeroWeightSingletons)
        print("bCubed recall, precision, fscore = {0:.3f}, {1:.3f}, {2:.3f}\n".format(recall, precision, fscore))


    def evaluateMUC(self):
        ''' main method which sets up the clusters by reading in files and passes the clusters to the MUC algorithm '''
        print("Calculating MUC...")
        recall, precision, fscore = metrics.MUC(self.clusterDict, self.goldEvaluator)
        print("MUC recall, precision, fscore = {0:.3f}, {1:.3f}, {2:.3f}\n".format(recall, precision, fscore))


    def evaluatePairWise(self):
        ''' main method which sets up the clusters by reading in files and passes the clusters to the pair-wise algorithm '''
        print("Calculating pair-wise...")
        recall, precision, fscore = metrics.pairWise(self.clusterDict, self.goldEvaluator)
        print("pair-wise recall, precision, fscore = {0:.3f}, {1:.3f}, {2:.3f}\n".format(recall, precision, fscore))


    def evaluatePurity(self):
        ''' main method which sets up the clusters by reading in files and passes the clusters to the cluster purity algorithm '''
        print("Calculating purity...")
        purity  = metrics.clusterPurity(self.clusterDict, self.goldEvaluator)
        print("cluster purity = {0:.3f}\n".format(purity))




if __name__ == "__main__":
    import sys
    import optparse

    parser = optparse.OptionParser()
    parser.add_option('-g', action='store', dest='goldSetsFile', help="the gold cognate file (deafult: GoldSetsAlgonquian.txt)", default="../Data/GoldSetsAlgonquian.txt")
    parser.add_option('-i', action='store', dest='evalFile', help="the file to evaluate")

    parser.add_option('--bCubed', action='store_true', dest='bCubed', help="flag to use for bCubed evaluation.", default=False)
    parser.add_option('-z', action='store_true', dest='zeroWeightSingletons', help="flag to zero-weight singletons with bCubed. default=False.", default=False)

    parser.add_option('--MUC', action='store_true', dest='MUC', help="flag to use for MUC evaluation.", default=False)
    parser.add_option('--pairWise', action='store_true', dest='pairWise', help="flag to use for pairWise evaluation.", default=False)
    parser.add_option('--purity', action='store_true', dest='purity', help="flag to use for purity evaluation.", default=False)


    parser.add_option('-o', action='store_true', dest='systemOutput', help="flag if using output with proto sets and svm additions", default=False)
    parser.add_option('-d', action='store_true', dest='defSets', help="flag if using output of just definition sets", default=False)
    parser.add_option('--maxRecall', action='store_true', dest='maxRecall', help="the flag if want to evaluate the max recall baseline clustering, rather than output files.", default=False)
    parser.add_option('--maxPrecision', action='store_true', dest='maxPrecision', help="the flag if want to evaluate the max precision baseline clustering, rather than output files.", default=False)
    parser.add_option('--putTogether', action='store_true', dest='putTogether', help="the flag if want to evaluate the output sets clustered all together into one cluster.", default=False)


    parser.add_option('-s', '--small', action='store_true', dest='smallDataSets', help="flag if want to use the small language files. For debugging in a shorter amount of time.")

    options, args = parser.parse_args()
    
    if options.evalFile is None and (options.systemOutput or options.defSets or options.putTogether):
        print("please provide cognate output file!")
        exit()

    if options.putTogether:
        clusterCreator = PutTogetherClusterCreator(options.smallDataSets, options.evalFile)
    elif options.systemOutput:
        clusterCreator = SystemOutputClusterCreator(options.smallDataSets, options.evalFile)
    elif options.defSets:
        clusterCreator = DefSetClusterCreator(options.smallDataSets, options.evalFile)
    elif options.maxRecall:
        clusterCreator = MaxRecallClusterCreator(options.smallDataSets, None)
    elif options.maxPrecision:
        clusterCreator = MaxPrecisionClusterCreator(options.smallDataSets, None)
    elif options.maxPrecision:
        clusterCreator = MaxPrecisionClusterCreator(options.smallDataSets, None)
    else:
        sys.stderr.write("Must provide type of file to evaluate!\n")
        exit(-1)


    ce = CognateClustersEvaluator(options.goldSetsFile, clusterCreator.clusterDict)


    evalAll = True
    if options.bCubed:
        ce.evaluateBcubed(options.zeroWeightSingletons)
        evalAll = False
    if options.MUC:
        ce.evaluateMUC()
        evalAll = False
    if options.pairWise:
        ce.evaluatePairWise()
        evalAll = False
    if options.purity:
        ce.evaluatePurity()
        evalAll = False
    if evalAll:
        # if we don't signify any specific metrics to run, then just run them all
        ce.runAllEvaluationMetrics()


    #ce.printOutClusterings()        
