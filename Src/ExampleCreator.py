#!/usr/bin/env python3

''' 

classes used when creating the training and testing pair files
can create from gold sets, def sets, or from classified pairs

'''

from DefSetsReader import DefSetsReader
from CogSetFileReader import CogSetFileReader
from ClassifiedPairsReader import ClassifiedPairsReader
from LanguageDictParser import AlgonquianLanguageDictParser


import random
from collections import defaultdict


import sys

class ExampleCreator(object):
    # the default classificaiton symbols for positive and negative examples
    positiveClassification = "+"
    negativeClassification = "-"

    def __init__(self, outputFileName, noDefinitionsOutputFileName=None):
        self.outputFileName = outputFileName
        self.noDefinitionsOutputFileName = noDefinitionsOutputFileName # if this output file name is given, then the example creator will also
        # write the example pairs without definitions (this is the format needed by the substring featurizer)

    # the enter and exit methods are definied to automatically open and close the output file
    # these methods get called when executing a Python "with" statement
    def __enter__(self):
        if self.outputFileName is not None:
            self.examplePairsFileHandle = open(self.outputFileName, 'w')
        if self.noDefinitionsOutputFileName is not None:
            self.noDefinitionsExamplePairsFileHandle = open(self.noDefinitionsOutputFileName, 'w')
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.outputFileName is not None:
            self.examplePairsFileHandle.close()
        if self.noDefinitionsOutputFileName  is not None:
            self.noDefinitionsExamplePairsFileHandle.close()


    def writePositivePair(self, wordTuple1, wordTuple2):
        self.writePair(wordTuple1, wordTuple2, self.positiveClassification)

    def writeNegativePair(self, wordTuple1, wordTuple2):
        self.writePair(wordTuple1, wordTuple2, self.negativeClassification)

    def writePair(self, wordTuple1, wordTuple2, classification):
        # write two word tuples to the output file in their needed format(s)
        if self.outputFileName is not None:
            examplePair = "\t\t".join((classification, "\t".join(wordTuple1), "\t".join(wordTuple2)))
            self.examplePairsFileHandle.write(examplePair + "\n")
        if self.noDefinitionsOutputFileName is not None:            
            noDefinitionExamplePair = "\t".join((classification, wordTuple1[1], wordTuple2[1]))
            self.noDefinitionsExamplePairsFileHandle.write(noDefinitionExamplePair + "\n")



class FromSetsExampleCreator(ExampleCreator):

    ''' writes to two files:
    the full info file has lines like:
    langAcc1\tword1\tdef1\t\tlangAcc2\tword2\def2

    the example pair file has lines like:
    classification word1 word2 (classification is either + or -)

    creates positive examples from a "gold" file (can also be a same def set file) and negative examples from language dicts

    '''

    def __init__(self, inputFileName, outputFileName, noDefinitionsOutputFileName, desiredNumberOfPositives, negativeRatio, useLangDictsForNegatives, 
                 family, fromDefSets, randomSeed=100):
        super().__init__(outputFileName, noDefinitionsOutputFileName)
        self.inputFileName = inputFileName
        self.desiredNumberOfPositives = desiredNumberOfPositives
        self.negativeRatio = negativeRatio
        self.useLangDictsForNegatives = useLangDictsForNegatives
        self.languageFamily = family
        self.fromDefSets = fromDefSets # True if input sets are def sets, False if input sets are cog sets
        self.randomSeed = randomSeed # if want to seed the random number generator so that the negative examples will always be the same. This just helps for replicability



    def run(self):
        # method to create a pair for all pairwise words in the same set

        random.seed(self.randomSeed) # this is used so that if we create the file again, it will be the same
        # the pairs created are still "random", this just helps with reproducibility

        if self.fromDefSets:
            self.createLanguageMappingsFromDefSets()
        else:
            self.createLanguageMappingsFromCogSets()

        sys.stderr.write("creating positive pairs...\n")
        if self.desiredNumberOfPositives == "all":
            self.createAllPositivePairs()
        else:
            self.desiredNumberOfPositives = int(self.desiredNumberOfPositives)
            self.createPositiveExamples()

        sys.stderr.write("Number of positive examples = {0}\n".format(self.numPositiveExamples))

        if self.useLangDictsForNegatives:
            self.readLanguageFiles()
            self.addLangDictWordsToMappings()

        sys.stderr.write("creating negative pairs...\n")
        self.createNegativeExamples()
        sys.stderr.write("Number of negative examples = {0}\n".format(self.numNegativeExamples))            

    def readLanguageFiles(self):
        if self.languageFamily == "algonquian":
            self.ldp = AlgonquianLanguageDictParser()
        elif self.languageFamily == "totonac":
            self.ldp = TotonacLanguageDictParser()
        else:
            sys.stderr.write("Unknown language family!\n")
            exit(-1)


    def addLangDictWordsToGivenMapping(self, langDict, mapping, langAcc):
        maxNum = max(mapping)
        newNum = maxNum + 1 # make sure new mapping numbers aren't already in the dict
        for word in sorted(langDict):
            if word in mapping:
                continue
            for defn in langDict[word]:
                newTuple = (langAcc, word, defn) 
                mapping[newNum] = [newTuple] # the word is its own set, i.e it is not a cognate or same def set word
                newNum += 1



    def createPositiveExamples(self):
        ''' method to create a certain number of positive examples (self.desiredNumberOfPositives) '''
        self.numPositiveExamples = 0
        self.createdPositives = set()
        sys.stderr.write("\n\n")
        while self.numPositiveExamples < self.desiredNumberOfPositives:
            sys.stderr.write("\033[F")
            sys.stderr.write("{0} / {1} pairs created\n".format(self.numPositiveExamples, self.desiredNumberOfPositives))
            self.createOnePositiveExample()
            self.numPositiveExamples += 1


    def createNegativeExamples(self):
        self.numNegativeExamples = 0
        self.createdNegatives = set()
        while self.numNegativeExamples < self.negativeRatio * self.numPositiveExamples:
            self.createOneNegativeExample()
            self.numNegativeExamples += 1
            #print("{0} negative examples created".format(self.numNegativeExamples))


    def getRandomTupleFromSetNum(self, setNum, mapping):
        wordTuples = mapping[setNum]
        index = random.randint(0, len(wordTuples) - 1)
        wordTuple = wordTuples[index]
        return wordTuple



class TwoLanguagesFromSetsExampleCreator(FromSetsExampleCreator):

    def __init__(self, inputFileName, outputFileName, noDefinitionsOutputFileName, desiredNumberOfPositives, negativeRatio, useLangDictsForNegatives, 
                 family, langAcc1, langAcc2, fromDefSets, randomSeed=100):
        super().__init__(inputFileName, outputFileName, noDefinitionsOutputFileName, desiredNumberOfPositives, negativeRatio, useLangDictsForNegatives, family,  fromDefSets, randomSeed=100)
        self.langAcc1 = langAcc1
        self.langAcc2 = langAcc2
        self.bothLangAccs = {langAcc1, langAcc2}



    def createLanguageMappingsFromDefSets(self):
        # creates a mapping for each language acc.
        # each mapping maps a set number to a list of wordTuples in that set which belong to the mapping's language
        self.mapping1 = defaultdict(list)
        self.mapping2 = defaultdict(list)
        self.reader = DefSetsReader()
        self.reader.readFile(self.inputFileName)
        for i, defSet in enumerate(self.reader):
            for wordTuple in defSet:
                acc = wordTuple[0]
                if acc == self.langAcc1:
                    self.mapping1[i].append(wordTuple)
                if acc == self.langAcc2:
                    self.mapping2[i].append(wordTuple)



    def createLanguageMappingsFromCogSets(self):
        # creates a mapping for each language acc.
        # each mapping maps a set number to a list of wordTuples in that set which belong to the mapping's language
        self.mapping1 = defaultdict(list)
        self.mapping2 = defaultdict(list)
        self.reader = CogSetFileReader(self.inputFileName)
        for cogNum in self.reader:
            cogSet = self.reader[cogNum]
            for wordTuple in cogSet:
                acc = wordTuple[0]
                if acc == self.langAcc1:
                    self.mapping1[cogNum].append(wordTuple)
                if acc == self.langAcc2:
                    self.mapping2[cogNum].append(wordTuple)



    def addLangDictWordsToMappings(self):
        self.addLangDictWordsToGivenMapping(self.ldp[self.langAcc1], self.mapping1, self.langAcc1)
        self.addLangDictWordsToGivenMapping(self.ldp[self.langAcc2], self.mapping2, self.langAcc2)


    def createAllPositivePairs(self):
        self.numPositiveExamples = 0
        self.allSetsList = set(self.mapping1.keys()) & set(self.mapping2.keys()) # make a set with all cognate set numbers in it.
        for num in self.allSetsList:
            for wordTuple1 in self.mapping1[num]:
                for wordTuple2 in self.mapping2[num]:
                    self.writePositivePair(wordTuple1, wordTuple2)
                    self.numPositiveExamples += 1


    def createPositiveExamples(self):
        ''' method to create a certain number of positive examples (self.desiredNumberOfPositives) '''
        self.allSetsList = set(self.mapping1.keys()) & set(self.mapping2.keys()) # make a set with all cognate set numbers in it.
        self.numsToUse = sorted(set(self.mapping1.keys()) & set(self.mapping2.keys()) , reverse=True) # make a list with all cognate set numbers in it.
        # as we create positive pairs, we want to make sure every cognate set is used at least once
        super().createPositiveExamples()


    def createOnePositiveExample(self):
        while True:
            if not self.numsToUse == []:
                # while there is still a set to use that hasn't been used yet
                setNum = self.numsToUse.pop()
            else:
                # all sets have been used at least once so use any random set for remaining pairs
                setNum = random.choice(self.allSetsList)


            wordTuple1 = self.getRandomTupleFromSetNum(setNum, self.mapping1)
            wordTuple2 = self.getRandomTupleFromSetNum(setNum, self.mapping2)

            if (wordTuple1, wordTuple2) in self.createdPairs:
                # already added this pair (odds low but could happen)
                continue
            else:
                break

        self.writePositivePair(wordTuple1, wordTuple2)
        self.createdPositives.add((wordTuple1, wordTuple2))


        '''
    def createPositivePairsForTupleList(self, tupleList):
        # given a single list of word tuples, create all pairwise full info and example pairs and write to
        # their respective files.
        for i, wordTuple1 in enumerate(tupleList):
            acc1, word1, defn1 = wordTuple1
            if not acc1 in self.bothLangAccs:
                continue
            j = i + 1
            while j < len(tupleList):
                wordTuple2 = tupleList[j]
                acc2, word2, defn2 = wordTuple2
                if not acc2 in self.bothLangAccs:
                    j += 1
                    continue
                if acc2 == acc1 and self.langAcc1 != self.langAcc2:
                    # if we aren't looking for pairs from the same language, continue
                    j += 1
                    continue
                if acc1 == self.langAcc1:
                    # we need to make sure the pair is printed in the same order every time, with self.langAcc1 tuple being first
                    self.writePositivePair(wordTuple1, wordTuple2 )
                else:
                    self.writePositivePair(wordTuple2, wordTuple1)
                self.numPositiveExamples += 1
                j += 1
                '''

    def createOneNegativeExample(self):
        # creates a single negative example
        nums1 = list(self.mapping1.keys())
        nums2 = list(self.mapping2.keys())
        while True:
            setNum1 = random.choice(nums1)
            setNum2 = random.choice(nums2)
            if setNum2 == setNum1:
                # if from the same set, then not negative, so try again
                continue

            wordTuple1 = self.getRandomTupleFromSetNum(setNum1, self.mapping1)
            wordTuple2 = self.getRandomTupleFromSetNum(setNum2, self.mapping2)
            if (wordTuple1, wordTuple2) in self.createdNegatives:
                # want to create new distinct examples
                continue

            # break out of the loop if we found a pair of words that are not in the same set and not already used
            break

        self.writeNegativePair(wordTuple1, wordTuple2)
        self.createdNegatives.add((wordTuple1, wordTuple2))



class AllLangsFromSetsExampleCreator(FromSetsExampleCreator):

    languageSimilarityDict = {}

    def createLanguageMappingsFromDefSets(self):
        # the mapping maps a set number to a list of wordTuples in that set
        self.mapping = defaultdict(list)
        self.reader = DefSetsReader()
        self.reader.readFile(self.inputFileName)
        for i, defSet in enumerate(self.reader):
            for wordTuple in defSet:
                self.mapping[i].append(wordTuple)


    def createLanguageMappingsFromCogSets(self):
        # the mapping maps a set number to a list of wordTuples in that set
        self.mapping = defaultdict(list)
        self.reader = CogSetFileReader(self.inputFileName)
        for cogNum in self.reader:
            cogSet = self.reader[cogNum]
            for wordTuple in cogSet:
                self.mapping[cogNum].append(wordTuple)


    def addLangDictWordsToMapping(self):
        for lang in self.ldp.getLangs():
            self.addLangDictWordsToMapping(self.ldp[lang], self.mapping, lang)            


    def createAllPositivePairs(self):
        self.numPositiveExamples = 0
        for i in self.mapping:
            wordSet = self.mapping[i]
            self.createPositivePairsForTupleList(wordSet) 


    def createPositivePairsForTupleList(self, tupleList):
        # given a single list of word tuples, create all dissimilar pairs
        for i, wordTuple1 in enumerate(tupleList):
            acc1, word1, defn1 = wordTuple1
            j = i + 1
            while j < len(tupleList):
                wordTuple2 = tupleList[j]
                acc2, word2, defn2 = wordTuple2
                if not self.areSimilarLanguages(acc1, acc2):
                    self.writePositivePair(wordTuple1, wordTuple2)
                    self.numPositiveExamples += 1
                j += 1


    def createPositiveExamples(self):
        ''' method to create a certain number of positive examples (self.desiredNumberOfPositives) '''
        self.similarSets = set() # keep track of how many sets only contain words from similar languages
        self.allSetsList = sorted(self.mapping.keys())
        self.numsToUse = sorted(self.mapping.keys(), reverse=True) # make a list with all cognate set numbers in it.
        # as we create positive pairs, we want to make sure every cognate set is used at least once
        super().createPositiveExamples()

    def createOnePositiveExample(self):
        while True:
            if not self.numsToUse == []:
                # while there is still a set to use that hasn't been used yet
                setNum = self.numsToUse.pop()
            else:
                # all sets have been used at least once so use any random set for remaining pairs
                setNum = random.choice(self.allSetsList)
            wordSet = self.mapping[setNum]

            wordTuple1, wordTuple2 = self.getWordsFromDissimilarLanguages(wordSet)

            if wordTuple1 is None:
                # if wordTuple is None this means no single word pair of dissimilar languages in the entire set
                self.similarSets.add(setNum)
                continue


                # already added this pair (odds low but could happen)
                continue
            else:
                break

        self.writePositivePair(wordTuple1, wordTuple2)
        self.createdPositives.add((wordTuple1, wordTuple2))


    def getWordsFromDissimilarLanguages(self, wordSet):
        ''' given a set of word tuples, returns two word tuples for languages that are not similar.
        Useful since we do not want to create example pairs from similar languages, as they are too easy.'''
        count = 0
        while True:
            wordNum1 = random.randint(0, len(wordSet)-1)
            wordNum2 = random.randint(0, len(wordSet)-1)

            if wordNum1 == wordNum2:
                continue

            # now we have two different numbers in the set to grab a word from

            wordTuple1 = wordSet[wordNum1]
            wordTuple2 = wordSet[wordNum2]

            if not self.areSimilarLanguages(wordTuple1[0], wordTuple2[0]):
                # if the languages of the two words are not similar, then we can break from the loop,
                # otherwise, try again to find words
                break
            count +=1

            if count > 100:
                # if we have tried 100 times to randomly find a word pair from dissimilar languages in this set,
                # then just look at every possible word pair exhaustively
                wordTuple1, wordTuple2 = self.findDissimilarWords(wordSet)
                if wordTuple1 is None:
                    # there does not exist a pair of 
                    break

        return wordTuple1, wordTuple2


    def findDissimilarWords(self, wordSet):
        ''' given a word set, look through every possible word pair to try and find a pair from dissimilar languages.
        if none are found, then return None, None '''
        i = 0
        while i < len(wordSet):
            wordTupleI = wordSet[i]
            j = i + 1
            while j < len(wordSet):
                wordTupleJ = wordSet[j]
                if not self.areSimilarLanguages(wordTupleI[0], wordTupleJ[0]):
                    return wordTuple1, wordTuple2
                j += 1
            i += 1
        return None, None


    def areSimilarLanguages(self, lang1, lang2):
        ''' given two languages, returns if they are similar or not, based on self.languageSimilarityDict mapping '''
        if lang1 == lang2:
            # trivially similar
            return True
        if not lang1 in self.languageSimilarityDict or not lang2 in self.languageSimilarityDict:
            # if either is not in the language to island mapping, then for sure not similar
            return False
        else:
            # return if they are mapped to the same island or not
            return self.languageSimilarityDict[lang1] == self.languageSimilarityDict[lang2]


    def createOneNegativeExample(self):
        # creates a single negative example
        nums = list(self.mapping.keys())
        while True:
            setNum1 = random.choice(nums)
            setNum2 = random.choice(nums)
            if setNum2 == setNum1:
                # if from the same set, then not negative, so try again
                continue

            wordTuple1 = self.getRandomTupleFromSetNum(setNum1, self.mapping)
            wordTuple2 = self.getRandomTupleFromSetNum(setNum2, self.mapping)
            if (wordTuple1, wordTuple2) in self.createdNegatives or (wordTuple2, wordTuple1) in self.createdNegatives :
                # want to create new distinct examples
                continue

            # break out of the loop if we found a pair of words that are not in the same set and not already used
            break

        self.writeNegativePair(wordTuple1, wordTuple2)
        self.createdNegatives.add((wordTuple1, wordTuple2))


class SimilarityInfoAllLangsFromSetsExampleCreator(AllLangsFromSetsExampleCreator):
    # this version uses just information from Wikipedia
    languageSimilarityDict = dict([("ARS", "ELLICEAN"), ("BGO", "ELLICEAN"), ("KWR", "ELLICEAN"), ("KAP", "ELLICEAN"),
                             ("LAU", "ELLICEAN"), ("NGG", "ELLICEAN"), ("OJA", "ELLICEAN"), ("PIL", "ELLICEAN"),
                             ("REN", "ELLICEAN"), ("ROV", "ELLICEAN"), ("SAA", "ELLICEAN"), ("SIK", "ELLICEAN"),
                             ("TAK", "ELLICEAN"), ("TIK", "ELLICEAN"), ("VRA", "ELLICEAN"),
                             ("MAE", "FUTUNIC"), ("MFA", "FUTUNIC"), ("MOT", "FUTUNIC"), ("MTA", "FUTUNIC"),
                             ("NGU", "FUTUNIC"), ("PMA", "FUTUNIC"), ("RAG", "FUTUNIC"), ("WFU", "FUTUNIC"), ("PUK", "FUTUNIC"),
                             ("AIT", "TAHITIC"),  ("MOR", "TAHITIC"), ("MIA", "TAHITIC"), ("MKI", "TAHITIC"), 
                             ("MRA", "TAHITIC"), ("PEN", "TAHITIC"), ("RAR", "TAHITIC"),
                             ("SAM", "SAMOIC"), ("TOK", "SAMOIC"),
                             ("TON", "TONGIC"), ("NIU", "TONGIC"),
                             ("HAW", "MARQUESIC"), ("MQA", "MARQUESIC")])



class ClassifiedPairExampleCreator(ExampleCreator):

    def __init__(self, inputFileName, outputFileName, noDefinitionsOutputFileName, sameLang=False):
        super().__init__(outputFileName, noDefinitionsOutputFileName)        
        self.inputFileName = inputFileName
        self.sameLang = sameLang

    def run(self):
        sys.stderr.write("Reading classified pairs...\n")
        classifiedReader = ClassifiedPairsReader(self.inputFileName, self.sameLang) # if sameLang is true then "bothWays" from the pairReader is true
        sys.stderr.write

        sys.stderr.write("\n")

        for i, wordTuple in enumerate(classifiedReader):
            sys.stderr.write("\033[F")
            sys.stderr.write("Creating for word {0} / {1}\n".format(i, len(classifiedReader)))

            otherTuplesWithScores = classifiedReader[wordTuple]
            for other in otherTuplesWithScores:
                otherTuple = other[:-1]
                self.writeNegativePair(wordTuple, otherTuple)





