#!/usr/bin/env python3

''' this script will read in the output of proto sets and additions, and print out annotations for all words found in a set '''


from collections import defaultdict

from GoldEvaluator import GoldEvaluator
from DefSetsReader import DefSetsReader

class OutputAnnotator(object):
    ''' this class will take a given output file and annotate it but putting together all words (from primary or secondary cognates) of a given set together if they 
    are part of the same Gold Set '''
    
    def __init__(self, goldSetsFile):
        ''' intitialize by passing in a gold standard, most likely GoldSetsAlgonquian.txt'''
        self.goldEvaluator = GoldEvaluator(goldSetsFile)


    def partitionIntoGoldSets(self, allWords):
        # this method looks at all words of a same def set, and those words that belong to the same gold set are put into the same set.
        partitions = defaultdict(set)
        for i, wordTuple in enumerate(allWords):
            j = i+1
            while j < len(allWords):
                wordTuple2 = allWords[j]
                if wordTuple == wordTuple2:
                    j += 1
                    continue
                if self.goldEvaluator.areCognatesDirty(wordTuple[:3], wordTuple2[:3]):
                    cogNum = self.goldEvaluator.getCogNumFromTuple(wordTuple[:3])
                    #print("cognates: {0}, {1}. cogNum = {2}".format(wordTuple[:3], wordTuple2[:3], cogNum))
                    if cogNum is None:
                        print("none set: {0}, {1}".format(wordTuple[:3], wordTuple2[:3]))
                        j += 1
                        continue
                    #cleanTuple = self.goldEvaluator.cleanTuple(wordTuple[:3])
                    #cleanTuple2 = self.goldEvaluator.cleanTuple(wordTuple2[:3])
                    #partitions[cogNum].add(cleanTuple)
                    #partitions[cogNum].add(cleanTuple2)                    
                    partitions[cogNum].add(wordTuple)
                    partitions[cogNum].add(wordTuple2)                    
                    self.foundNums.add(cogNum)
                j += 1
        for cogNum in partitions:
            self.allPartitions[cogNum].append(partitions[cogNum])


    def annotateList(self, allWords):
        foundSets = defaultdict(set)
        #print("Proposed Set:")
        for i, wordTuple in enumerate(allWords):
            cogNum = self.goldEvaluator.getCogNumFromTuple(wordTuple)
            if cogNum is not None:
                foundSets[cogNum].add(wordTuple)
            toPrint = wordTuple + (str(cogNum).zfill(4),)
            print("\t".join(toPrint))
        for setNum in sorted(foundSets):
            foundLength = len(foundSets[setNum])
            goldLength = len(self.goldEvaluator.getCogSetFromCogNum(setNum))
            if foundLength < goldLength:
                self.printRestOfGoldSet(setNum, foundSets[setNum])


    def printRestOfGoldSet(self, setNum, foundTuples):
        #cleanTuples = set(map(self.goldEvaluator.cleanTuple, foundTuples))
        #goldSet = self.goldEvaluator.getCogSetFromCogNum(setNum)
        goldSet = self.goldEvaluator.dirtyNumToCognateSet[setNum]
        print("Gold set {0}:".format(str(setNum).zfill(4)))
        for goldTuple in sorted(goldSet):
            #if goldTuple in cleanTuples:
            if goldTuple in foundTuples:
                continue
            print("\t".join(goldTuple))


    def printPartitions(self):
        for cogNum in sorted(self.allPartitions):
            for partition in self.allPartitions[cogNum]:
                print("Set Number {0}".format(str(cogNum).zfill(4)))
                for wordTuple in sorted(partition):#, key=itemgetter(0)):
                    print("\t".join(wordTuple))
                print('\n')


    def printPartitionsNoCogNum(self):
        # similar to printParittions, but the cogNumber is not printed before the set and only one newline between
        # i.e. a "Def Set" instead of a "Gold Set"
        for cogNum in sorted(self.allPartitions):
            for partition in self.allPartitions[cogNum]:
                print("Def")
                for wordTuple in sorted(partition):
                    print("\t".join(wordTuple))
                print()



    def printMissingSets(self):
        for cogNum in sorted(self.goldEvaluator.numToCognateSet):
            if cogNum in self.foundNums:
                continue
            print("Set Number {0}".format(str(cogNum).zfill(4)))
            for wordTuple in sorted(self.goldEvaluator.getDirtyCogSetFromCogNum(cogNum), key=itemgetter(0)):
                print("\t".join(wordTuple))
            print('\n')


    def evaluateFoundSets(self):
        numFullyFound = 0
        numPartiallyFound = 0
        numAtLeastPartiallyFound = len(self.foundNums)
        for cogNum in self.foundNums:
            partitions = self.allPartitions[cogNum]
            foundLength = max([len(x) for x in partitions])
            goldLength = len(self.goldEvaluator.getCogSetFromCogNum(cogNum))
            if foundLength == goldLength:
                numFullyFound +=1
            else:
                numPartiallyFound +=1

        numGold = len(self.goldEvaluator.numToCognateSet)
        print("num fully found sets = {0}".format(numFullyFound))
        print("percent fully found sets = {0:.3f}".format(numFullyFound/numGold))
        print("num partially found sets = {0}".format(numPartiallyFound))
        print("num at least partially found sets = {0}".format(numAtLeastPartiallyFound))
        print("percent at least partially found sets = {0:.3f}".format(numAtLeastPartiallyFound/numGold))
        print("num sets in gold = {0}".format(numGold))


    def printNumbersOfFoundSets(self):
        # this method simply prints out the numbers of the sets found, line by line.
        # to make it easy to compare the found sets of two systems
        for cogNum in sorted(self.foundNums):
            print(cogNum)


class DefSetAnnotator(OutputAnnotator):
    ''' class to use if the input file to annotate is a def sets file '''
    def partitionFile(self, cognateFileToAnnotate):
        self.allPartitions = defaultdict(list)
        self.foundNums = set()
        parser = DefSetsReader()
        parser.readFile(cognateFileToAnnotate)
        for defSet in parser:
            allWords = defSet.wordTupleList
            self.partitionIntoGoldSets(allWords)


    def annotateFile(self, cognateFileToAnnotate):
        parser = DefSetsReader()
        parser.readFile(cognateFileToAnnotate)
        for defSet in parser:
            allWords = defSet.wordTupleList
            print(defSet.defn)
            self.annotateList(allWords)
            print("")

if __name__ == "__main__":
    import sys
    import optparse

    parser = optparse.OptionParser()
    parser.add_option('-g', action='store', dest='goldFile', help="the gold cognate file (deafult: GoldSetsAlgonquian.txt)", default="../Data/GoldSetsAlgonquian.txt")
    parser.add_option('-i', action='store', dest='inputFile', help="name of file to partitino/annotate")

    parser.add_option('-f', action='store_true', dest='printFoundSets', help="flag if want to print found sets as Gold Sets.",default=False)
    parser.add_option('-n', action='store_true', dest='printFoundNumbers', help="flag if want to print just the numbers of the found sets.",default=False)
    parser.add_option('-c', action='store_true', dest='printClusters', help="flag if want to print found sets as Def Sets. i.e. the 'Oracle' Word List system",default=False)
    parser.add_option('-m', action='store_true', dest='printMissingSets', help="flag if want to print missing gold sets.", default=False)

    parser.add_option('-e', action='store_true', dest='evaluateFoundSets', help="flag if want to evaluate sets for number of partial/fully found.", default=False)
    parser.add_option('-a', action='store_true', dest='annotate', help="flag if want to annotate the file with cogNums, and when partial sets are found, print the rest.", default=False)


    options, args = parser.parse_args()

    if options.inputFile is None:
        sys.stderr.write("Must provide file name!\n")
        exit(-1)

    ca = DefSetAnnotator(options.goldFile)
   

    if options.printFoundSets:
        ca.partitionFile(options.inputFile)
        ca.printPartitions()

    if options.printFoundNumbers:
        ca.partitionFile(options.inputFile)
        ca.printNumbersOfFoundSets()

    if options.printClusters:
        ca.partitionFile(options.inputFile)
        ca.printPartitionsNoCogNum()

    if options.printMissingSets:
        ca.partitionFile(options.inputFile)
        ca.printMissingSets()

    if options.evaluateFoundSets:
        ca.partitionFile(options.inputFile)
        ca.evaluateFoundSets()

    if options.annotate:
        ca.annotateFile(options.inputFile)

