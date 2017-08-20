#!/usr/bin/env python3

''' this script reads in words pairs, features, and svm scores, and prints them in a formatted fashion '''


from GoldEvaluator import GoldEvaluator

from collections import defaultdict
import sys

class OutputFormatter(object):

    def __init__(self, svmOutputFile, wordPairsFile, featuresFile, restrict2=None):
        ''' takes three file names and reads them into sets. 
        The svmOutput file has a real number on each line.
        The features file has the feature scores of a word pair on each line.
        The wordPairs file has Acc\tWord\tDefinition\t\tAcc2\tWord2\tDefinifiton2   This is different than the old way (Nov. 14) '''

        self.svmOutputFile = svmOutputFile
        self.featuresFile = featuresFile
        self.wordPairsFile = wordPairsFile
        self.restrict2 = restrict2

        sys.stderr.write("\nassociating scores with words and features...\n")
        self.associateScores()


    def associateScores(self):
        numLines = 0
        with open(self.svmOutputFile) as file:
            for line in file:
                numLines += 1

        sys.stderr.write("\n\n")
        self.scoreMapping = defaultdict(list)
        count = 0
        with open(self.svmOutputFile) as predsFile:
            with open(self.featuresFile) as featuresFile:
                with open(self.wordPairsFile) as pairsFile:
                    for svmScore, features, pair in zip(predsFile, featuresFile, pairsFile):
                        count += 1
                        sys.stderr.write("\033[F")
                        sys.stderr.write("{0} / {1} = {2:.2f}% lines looked at...\n".format(count, numLines, 100*count/numLines))
                        svmScore = float(svmScore.strip())
                        features = features.strip()
                        classification, wordLine1, wordLine2 = pair.strip().split('\t\t')
                        wordTuple1 = tuple(wordLine1.split("\t"))
                        wordTuple2 = tuple(wordLine2.split("\t"))

                        if self.restrict2 is not None:
                            # if we want to restrict the second languages to a certain lang
                            lang2 = wordTuple2[0]
                            if lang2 != self.restrict2:
                                continue
                        pairTuple = (wordTuple1, wordTuple2)
                        self.scoreMapping[svmScore].append((features, pairTuple))


    def printSVMScores(self):
        ''' prints out the svm scores in order they were read. for debugging '''
        for score in sorted(self.svmOutputs, reverse=True):
            print(score)
        print("\n==========================\n")
        for score in sorted(self.scoreMapping, reverse=True):
            print(score)
        

    def printPairsWithGivenScore(self, score):
        mappingList = self.scoreMapping[score]
        for mapping in mappingList:
            features = mapping[0]
            wordTuple1, wordTuple2 = mapping[1]
            print("SVM Value: " + str(score))
            print(features)
            print("\t".join(wordTuple1))
            print("\t".join(wordTuple2))
            print()


    def printPassedPairs(self):
        count = 0
        sys.stderr.write("\n\n")
        for score in sorted(self.scoreMapping, reverse=True):
            count += 1
            sys.stderr.write("\033[F")
            sys.stderr.write("{0} / {1} scores printed\n".format(count, len(self.scoreMapping)))

            if score < 0:
                break # since list is sorted, as soon is one is below 0 they all will be
            self.printPairsWithGivenScore(score)


    def printNegativePairs(self):
        for score in sorted(self.scoreMapping, reverse=True):
            if score >= 0:
                continue # don't print if score is positve AKA passed
            self.printPairsWithGivenScore(score)


    def printAllPairs(self):
        count = 0
        sys.stderr.write("\n")        
        for score in sorted(self.scoreMapping, reverse=True):
            count += 1
            sys.stderr.write("\033[F")
            sys.stderr.write("printing score {0} / {1}\n".format(count, len(self.scoreMapping)))
            self.printPairsWithGivenScore(score)



class RestrictedOutputFormatter(OutputFormatter):
    # this class prints out a simplified version of the pairs, without scores or feature values, and
    # only allowing a word or cog set to be printed once

    def __init__(self, svmOutputFile, wordPairsFile, featuresFile, restrict2=None, goldFile1=None, goldFile2=None):
        if goldFile1 is not None:
            self.gold1 = True
            self.goldReader1 = GoldEvaluator(goldFile1)
            self.goldSets1 = set()
        else:
            self.gold1 = False

        if goldFile2 is not None:
            self.gold2 = True
            self.goldReader2 = GoldEvaluator(goldFile2)
            self.goldSets2 = set()
        else:
            self.gold2 = False

        super().__init__(svmOutputFile, wordPairsFile, featuresFile, restrict2)
            

    def printPairsWithGivenScore(self, score):
        mappingList = self.scoreMapping[score]
        self.usedWords1 = set()
        self.usedWords2 = set()
        for mapping in mappingList:
            wordTuple1, wordTuple2 = mapping[1]

            # if either word comes from a gold set that has already been used, do not print this pair
            if self.gold1 and self.alreadyInGold(self.goldReader1, self.goldSets1, wordTuple1):
                #print("word tuple 1 = {0} in gold set {1}".format(wordTuple1, self.goldReader1.getCogNumFromTuple(wordTuple1)))
                continue
            if self.gold2 and self.alreadyInGold(self.goldReader2, self.goldSets2, wordTuple2):
                #print("word tuple 2 = {0} in gold set {1}".format(wordTuple2, self.goldReader2.getCogNumFromTuple(wordTuple2)))
                continue

            # if either word has already been used, do not print this pair
            if self.alreadyUsedWord(self.usedWords1, wordTuple1):
                #print("word tuple 1 already used = {0}".format(wordTuple1))
                continue
            if self.alreadyUsedWord(self.usedWords2, wordTuple2):
                #print("word tuple 2 already used = {0}".format(wordTuple2))
                continue

            print("\t".join(wordTuple1))
            print("\t".join(wordTuple2))
            print()


    def alreadyInGold(self, goldReader, goldSets, wordTuple):
        goldNum = goldReader.getCogNumFromTuple(wordTuple)
        if goldNum is not None:
            if goldNum in goldSets:
                return True
            else:
                goldSets.add(goldNum)
        return False

    def alreadyUsedWord(self, usedWords, wordTuple):
        if wordTuple in usedWords:
            return True
        else:
            usedWords.add(wordTuple)


if __name__ == "__main__":
    import optparse
    
    
    parser = optparse.OptionParser()
    parser.add_option('-s', action='store', dest='svmOutput', help="Required: the svm output file.")
    parser.add_option('-p', action='store', dest='wordPairs', help="Required: the corresponding word pairs file.")
    parser.add_option('-f', action='store', dest='features', help="Required: the corresponding svm features file.")
    parser.add_option('-a', action='store_true', dest='allPairs', help="Optional: use if want to print all pairs, not just passed pairs.", default=False)
    parser.add_option('-n', action='store_true', dest='negativePairs', help="Optional: use if want to print negative score pairs, not passed(positive score) pairs.", default=False)
    parser.add_option('-d', action='store_true', dest='debug', help="debug prints extra", default=False)


    parser.add_option('--r2', action='store', dest='restrict2', help="If want to restrict the second words to a specific language family", default=None)


    parser.add_option('-r', action='store_true', dest='restrict', help="If want to restrict words and cogNums to appear only once in the output", default=False)
    parser.add_option('--g1', action='store', dest='goldFile1', help="Gold file name for the first words", default=None)
    parser.add_option('--g2', action='store', dest='goldFile2', help="Gold file name for the second words", default=None)
                      
    options, args = parser.parse_args()
                

    if options.svmOutput is None or options.wordPairs is None or options.features is None:
        parser.print_help()
        exit()


    if options.restrict:
        formatter = RestrictedOutputFormatter(options.svmOutput, options.wordPairs, options.features, options.restrict2, options.goldFile1, options.goldFile2)
    else:
        formatter = OutputFormatter(options.svmOutput, options.wordPairs, options.features, options.restrict2)
                      
    
    sys.stderr.write("\nwriting output...\n")
    if options.allPairs:
        formatter.printAllPairs()
    elif options.negativePairs:
        formatter.printNegativePairs()
    else:
        formatter.printPassedPairs()

    if options.debug:
        formatter.printSVMScores()
