#!/usr/bin/env python3
''' this module will contain the classes and methods needed to take words and definition pairs and create the General feature values '''


from StopWords import EnglishStopWords, SpanishStopWords
from WordNetFileHandler import WordNetFileHandler

from UniToASJPConverter import uniToASJP
from UniToALINEConverter import uniToALINE
from alignmentFeatures import getAlignmentFeatures, lookUpWordPairStrict
import binaryReadAndWrite

import DefinitionCleaner

import StringSimilarity
import sys
import time

from gensim.models import Word2Vec as w2v
#from gensim.models.keyedvectors import KeyedVectors as w2v

import editdistance


DATA_PATH = "../Data"

# download from https://code.google.com/archive/p/word2vec/
ENGLISH_VECTORS = "GoogleNews-vectors-negative300.bin.gz"

# download from http://crscardellino.me/SBWCE/
SPANISH_VECTORS = "SBW-vectors-300-min5.bin"

class GeneralFeaturizer(object):

    # define different feature sets
    # each type includes the previous type. Building up from simple to most complicated
    phoneticFeatures = {10,13,14,15} #not including 11 and 12 (prefic and suffix)
    surfaceSemanticFeatures = {1,2,3,4} | phoneticFeatures
    wordNetFeatures = {5,6,7,8,9} | surfaceSemanticFeatures
    word2VecFeatures = {16,17} | wordNetFeatures
    word2VecFeaturesNoWordNet = {16,17} | surfaceSemanticFeatures
    allFeatures = phoneticFeatures | surfaceSemanticFeatures | wordNetFeatures | word2VecFeatures

    featureMapping = {"phonetic": phoneticFeatures, "surface":surfaceSemanticFeatures, "wordNet":wordNetFeatures, "word2Vec":word2VecFeatures, "word2VecNoWordNet":word2VecFeaturesNoWordNet}

    def __init__(self, definitionLanguage, alignFeaturesFile=None, featureNumbersToUse=allFeatures): # features 11,12 (prefix and suffix) off by default
        ''' loads the default files '''

        if definitionLanguage == "en":
            self.stopWords = EnglishStopWords()
            self.synonyms = WordNetFileHandler(DATA_PATH + "/en_synonyms.txt")
            self.forms = WordNetFileHandler(DATA_PATH + "/en_forms.txt")
            self.synsets = WordNetFileHandler(DATA_PATH + "/en_synsets.txt")
            self.hyperonyms = WordNetFileHandler(DATA_PATH + "/en_hyperonyms.txt")
            self.vectorsPath = DATA_PATH + "/" + ENGLISH_VECTORS
            
        elif definitionLanguage == "es":
            self.stopWords = SpanishStopWords()
            self.synonyms = WordNetFileHandler(DATA_PATH + "/es_synonyms.txt")
            self.forms = WordNetFileHandler(DATA_PATH + "/es_forms.txt")
            self.synsets = WordNetFileHandler(DATA_PATH + "/es_synsets.txt")
            self.hyperonyms = WordNetFileHandler(DATA_PATH + "/es_hyperonyms.txt")
            self.vectorsPath = DATA_PATH + "/" + SPANISH_VECTORS 

        # by default, features 11 and 12 (PREFIX and SUFFIX) are turned off
        if isinstance(featureNumbersToUse, str):
            if featureNumbersToUse in self.featureMapping:
                self.featureNumbersToUse = self.featureMapping[featureNumbersToUse]
            else:
                sys.stderr.write("Undefined feature number set: {0}!\n".format(featureNumbersToUse))
                exit(-1)
        else:
            self.featureNumbersToUse = featureNumbersToUse # a set of all feature numbers we want to use, default is all
        sys.stderr.write("Feature numbers being used: {0}\n".format(self.featureNumbersToUse))


        self.vowels = set('aeiou3EOI')
        self.initFeatureList()
        self.alignFeaturesFile = alignFeaturesFile
        self.readAlignmentFile()


    def readAlignmentFile(self):
        # this reads the pairs from the given alignment file, and populates self.alignmentFeaturesDict 
        if self.alignFeaturesFile is None:
            self.alignmentFeaturesDict = None
        else:
            sys.stderr.write("reading alignment file {0}...\n".format(self.alignFeaturesFile))
            t1 = time.time()
            self.alignmentFeaturesDict = binaryReadAndWrite.readFromBinary(self.alignFeaturesFile)
            sys.stderr.write("finished reading alignment file...\n")
            t2 = time.time()
            sys.stderr.write("time to read alignment file = {0:.2f}m\n".format((t2-t1)/60.0))


    def readAdditionalAlignmentFile(self, alignFeaturesFile):
        # this method is used when we use one featurizer to create features for multiple language pairs at the same time
        # i.e. when parallelizing. 
        # it reads in an additional alignment features file and adds those pairs to self.alignmentFeaturesDict

        if self.alignmentFeaturesDict is None:
            # if no alignmentFeaturesDict exists yet, just set it to an empty dictionary so it can be added to
            self.alignmentFeaturesDict = {}

        # now read the given alignFeaturesFile into a new dictionary
        sys.stderr.write("reading alignment file {0}...\n".format(alignFeaturesFile))
        t1 = time.time()
        newAlignmentFeaturesDict = binaryReadAndWrite.readFromBinary(alignFeaturesFile)
        sys.stderr.write("finished reading alignment file...\n")
        t2 = time.time()
        sys.stderr.write("time to read alignment file = {0:.2f}m\n".format((t2-t1)/60.0))

        # now update the overallalignment features dict to contain the new pairs
        self.alignmentFeaturesDict.update(newAlignmentFeaturesDict)


    def setWords(self, word1, word2, asjp1, asjp2, aline1, aline2, def1, def2, cleanDef1, cleanDef2, acc1, acc2,  classification=0):
        self.acc1 = acc1
        self.acc2 = acc2
        self.word1 = word1
        self.word2 = word2
        self.asjp1 = asjp1
        self.asjp2 = asjp2
        self.aline1 = aline1
        self.aline2 = aline2
        self.def1 = def1
        self.def2 = def2
        self.cleanDef1 = cleanDef1
        self.cleanDef2 = cleanDef2
        self.splitDefs1 = self.splitDef(cleanDef1)
        self.splitDefs2 = self.splitDef(cleanDef2)
        self.classification = classification
        self.initLengthStats()
        self.initPrintForm()
        self.setKeywords()
        self.setForms()
        self.featureValues = [] # list keeping the feature values, in order of addition


    def splitDef(self, defn):
        ''' this method is used to split the definition on semi colons and return a list of all definitons. 
        We consider each part of the split to be a definitnion of the word. And the definition features fire
        if any of the definitoins meet a certain criteria 

        Definitions are already expected to be cleaned and joined by semicolons, because we would rather clean
        a definition once that is being used many times rather than clean it every time we featurize
        '''
        return defn.split(";")


    def setKeywords(self):
        # update March 16, keywords are now just content words
        self.keywords1 = {word for defn in self.splitDefs1 for word in defn.split() if word not in self.stopWords} # just the non-stop-words of all split definitions
        self.keywords2 = {word for defn in self.splitDefs2 for word in defn.split() if word not in self.stopWords}


    def setForms(self):
        self.forms1 = self.forms.at(self.keywords1) #| self.keywords1 # consider keyword to be form
        self.forms2 = self.forms.at(self.keywords2) #| self.keywords2


    def initLengthStats(self):
        ''' calculates the length of the words and the max word length and sets them as class variables since they are useful for multiple features '''
        self.lenWord1 = len(self.asjp1)
        self.lenWord2 = len(self.asjp2)
        self.maxLenWord = max(self.lenWord1, self.lenWord2)
        self.minLenWord = min(self.lenWord1, self.lenWord2)

    
    def initPrintForm(self):
        ''' this method sets self.printForm1 and self.printForm2. Needed since if we featurize against proto words that are only in
        ASJP, then that word does not have a UNI representation to print out. '''
        if self.word1 is None:
            self.printForm1 = self.asjp1
        else:
            self.printForm1 = self.word1

        if self.word2 is None:
            self.printForm2 = self.asjp2
        else:
            self.printForm2 = self.word2


    def addFeature(self, value):
        self.featureValues.append(value)


    def runAllFeatures(self):
        for featureMethod in self.featureListMethods:
            featureMethod()


    def getOutputLine(self):
        ''' creates the string of SVM features to be printed to the output file '''
        outputLine = str(self.classification)
        for i in range(len(self.featureValues)):
            featureNum = i + 1 # i starts at 0 but features start at 1
            outputLine += " " + str(featureNum) + ":"
            featureValue = round(self.featureValues[i], 15) # round to 15 spots like old perl output so easier to compare
            # turn 1.0 and 0.0 into ints so it matches the old perl output
            if featureValue == 1.0:
                featureValue = 1
            if featureValue == 0.0:
                featureValue = 0
            outputLine += str(featureValue)

        return outputLine


    def getReadableOutputLine(self):
        ''' creates the string of SVM features to be printed in a readable fashion '''
        outputLine = ""
        for i in range(len(self.featureValues)):
            outputLine += self.featureListNames[i] + " "
            featureValue = round(self.featureValues[i], 15)
            if featureValue == 1.0:
                featureValue = 1
            if featureValue == 0.0:
                featureValue = 0
            outputLine += str(featureValue) + "\n"

        return outputLine


    def getOutputPair(self):
        ''' creates the string of pairs to be printed to the output pairs file '''
        word1String = "{0}\t{1}\t{2}".format(self.acc1, self.printForm1, self.def1)
        word2String = "{0}\t{1}\t{2}".format(self.acc2, self.printForm2, self.def2)
        outputString = "\t\t".join((word1String, word2String))
        return outputString

            
    def printPairToFile(self, outputFile):
        pairToPrint = self.getOutputPair()
        #with open(outputFile, "a") as file: # open as append
        #    file.write(pairToPrint + "\n")
        self.pairsFile.write(pairToPrint + "\n")


    def printFeatures(self):
        lineToPrint = self.getOutputLine()
        print(lineToPrint)


    def printReadableFeatures(self):
        lineToPrint = self.getReadableOutputLine()
        print(lineToPrint)


    def printPair(self):
        pairToPrint = self.getOutputPair()
        print(pairToPrint)




    def runFeaturizerWithGivenWords(self, word1, word2, def1, def2, acc1, acc2):
        
        asjpWord1 = uniToASJP(word1)
        asjpWord2 = uniToASJP(word2)
        aline1 = uniToALINE(word1)
        aline2 = uniToALINE(word2)
        print("asjp1 = {0}, asjp2 = {1}".format(asjpWord1, asjpWord2))
        print("aline1 = {0}, aline2 = {1}".format(aline1, aline2))
        cleanDef1 = DefinitionCleaner.cleanDef(def1)
        cleanDef2 = DefinitionCleaner.cleanDef(def2)
        self.setWords(word1, word2, asjpWord1, asjpWord2, aline1, aline2, def1, def2,cleanDef1, cleanDef2, acc1, acc2)
        self.runAllFeatures()
        self.printPair()
        self.printFeatures()
        self.printReadableFeatures()



    def initFeatureList(self):
        ''' this method creates a list of feature methods that will be ran when "runAllFeatures" is called '''
        self.featureListMethods = []
        self.featureListNames = []

        if 1 in self.featureNumbersToUse:
            self.featureListMethods.append(self.definitionMatch) 
            self.featureListNames.append("DefinitionMatch") #1

        if 2 in self.featureNumbersToUse:
            self.featureListMethods.append(self.definitionWithOutStopWordsMatch)
            self.featureListNames.append("DefinitionContentMatch") #2

        if 3 in self.featureNumbersToUse:
            self.featureListMethods.append(self.invertedNormalizedEditDistanceDefinition) #3 
            self.featureListNames.append("InvertedNormalizedEditDistanceDefinition") 


        if set((4,5,6,7,8,9)) & self.featureNumbersToUse:
            self.featureListMethods.append(self.semanticFeatures)
            self.featureListNames.append("KeywordMatch") #4
            self.featureListNames.append("SynonymMatch") #5
            self.featureListNames.append("FormOfKeywordsMatch") #6
            self.featureListNames.append("SynonymOfFormsMatch") #7
            self.featureListNames.append("HyperonymOfKeywordsMatch") #8
            self.featureListNames.append("HyperonymOfFormsMatch") #9
        

        if 10 in self.featureNumbersToUse:
            self.featureListMethods.append(self.invertedNormalizedEditDistanceForm)
            self.featureListNames.append("InvertedNormalizedEditDistanceForm") #10

        if 11 in self.featureNumbersToUse:
            self.featureListMethods.append(self.normalizedPrefix)
            self.featureListNames.append("NormalizedLongestCommonPrefixForm") #11

        if 12 in self.featureNumbersToUse:
            self.featureListMethods.append(self.normalizedSuffix)
            self.featureListNames.append("NormalizedLongestCommonSuffixForm") #12


        if set((13,14)) & self.featureNumbersToUse:
            self.featureListMethods.append(self.alignmentFeatures)
            self.featureListNames.append("NormalizedAignedConsontantsForm") #13
            self.featureListNames.append("ALINE score") #14

        if 15 in self.featureNumbersToUse:
            self.featureListMethods.append(self.normalizedLCSForm)
            self.featureListNames.append("NormalizedLongestCommonSubsequenceForm") #15


        if 16 in self.featureNumbersToUse:
            t1 = time.clock()
            sys.stderr.write("reading vectors file...\n")
            self.model = w2v.load_word2vec_format(self.vectorsPath, binary=True) #
            t2 = time.clock()
            seconds = t2-t1
            minutes = seconds/60.0
            sys.stderr.write("finished reading vectors file in {0:.2f} seconds = {1:.2f} minutes!\n".format(seconds, minutes))

            self.featureListMethods.append(self.word2VecFeatures)
            self.featureListNames.append("Word2Vec n_Similarity Score") #16
            self.featureListNames.append("Word2Vec content words n_Similarity Score") #17


        
    def definitionMatch(self):
        # feature 1: do the definitions match exactly?
        # check all split defs of each one, and if there exists any exact match, fire the feature
        for def1 in self.splitDefs1:
            for def2 in self.splitDefs2:
                if def1 == def2:
                    self.addFeature(1)
                    return
        self.addFeature(0)



    def definitionWithOutStopWordsMatch(self):
        # feature 3: do the definitions match if exlcude stop words?
        # if any of the split defs match, fire the feature
        for def1 in self.splitDefs1:
            def1NoStop = self.stopWords.removeStopWords(def1)
            for def2 in self.splitDefs2:
                def2NoStop = self.stopWords.removeStopWords(def2)
                if def1NoStop == def2NoStop:
                    self.addFeature(1)
                    return
        self.addFeature(0)



    def invertedNormalizedEditDistanceDefinition(self):
        # new version of NED for definitoins. 
        # use the maximum value between all the split definitions
        maxInverted = 0 # inverted score goes between 0 and 1, so initialize max to 0
        for def1 in self.splitDefs1:
            words1 = def1.split()
            for def2 in self.splitDefs2:
                words2 = def2.split()
                defEditDistance = editdistance.eval(words1, words2)
                maxLenDef = max(len(words1), len(words2))
                normalized = defEditDistance / maxLenDef
                inverted = 1 - normalized
                if inverted > maxInverted:
                    maxInverted = inverted
        self.addFeature(maxInverted)


    def semanticFeatures(self):
        keywordsIntersect = self.keywordMatch()
        synonymsIntersect = self.synonymMatch(keywordsIntersect)
        formsIntersect = self.formMatch(keywordsIntersect)

        self.synonymOfFormMatch(formsIntersect, synonymsIntersect)

        synsets1, synsets2, hyperonyms1of2, hyperonyms2of1 = self.hyperonymMatch()

        if 9 in self.featureNumbersToUse:
            self.formHyperonymMatch(synsets1, synsets2, hyperonyms1of2, hyperonyms2of1)


    def addForIntersect(self, set1, set2):
        intersect = set1 & set2
        if intersect:
            self.addFeature(1)
        else:
            self.addFeature(0)


    def addForNonEmpty(self, testSet):
        ''' method that takes a set and adds a feature value of 1 or 0 depending on if the set is nonEmpty or not '''
        #print("test set = {0}".format(testSet))
        if testSet:
            self.addFeature(1)
        else:
            self.addFeature(0)


    def keywordMatch(self):
        keywordsIntersect = self.keywords1 & self.keywords2
        if 4 in self.featureNumbersToUse:
            self.addForNonEmpty(keywordsIntersect)
        return keywordsIntersect


    def formMatch(self, keywordsIntersect):
        trivialFormsMatches = self.forms.at(keywordsIntersect) # | keywordsIntersect  # to decouple this feature from keywordsMatch
        #print("forms1 = {0},\nforms2 = {1}".format(self.forms1, self.forms2))
        #print("trivForms")
        #print(trivialFormsMatches)
        formsIntersect = (self.forms1 & self.forms2) | (self.forms1 & self.keywords2) | (self.forms2 & self.keywords1)
        #print (self.forms1 & self.forms2) 
        #print(self.forms1 & self.keywords2) 
        #print(self.forms2 & self.keywords1)
        #print("formsIntersect = {0}".format(formsIntersect))
        nonTrivialFormsIntersect = formsIntersect - trivialFormsMatches # decouple from the keywords feature
        #print("nonTrivFormsIntersect")
        #print(nonTrivialFormsIntersect)
        if 9 in self.featureNumbersToUse:
            self.addForNonEmpty(nonTrivialFormsIntersect)
        return nonTrivialFormsIntersect


    def synonymMatch(self, keywordsIntersect):
        #trivialSynonymMatches =  keywordsIntersect #| self.synonyms.at(keywordsIntersect) 
        # if the defs have keyword matches, then those will necessarily lead to synonym matches, but we don't want to count these
        
        #synonyms1 = self.synonyms.at(self.keywords1) | self.keywords1 # the keywords are considerred a synonym
        #synonyms2 = self.synonyms.at(self.keywords2) | self.keywords2 
        #synonymsIntersect = synonyms1 & synonyms2
        synonyms1 = self.synonyms.at(self.keywords1) 
        synonyms2 = self.synonyms.at(self.keywords2) 

        #print("syns1")
        #print(synonyms1)
        #print("syns2")
        #print(synonyms2)
        
        synonymsIntersect = (synonyms1 & self.keywords2) | (synonyms2 & self.keywords1)
        #print("synsIntersect")
        #print(synonymsIntersect)
        if 4 in self.featureNumbersToUse:
            #self.addForNonEmpty(nonTrivialSynonymMatches)
            self.addForNonEmpty(synonymsIntersect)

        return synonymsIntersect


    def synonymOfFormMatch(self, formsIntersect, synonymsIntersect):
        #trivialSynonymOfFormMatches =  formsIntersect | synonymsIntersect #| self.synonyms.at(formsIntersect) 
        #trivialSynonymOfFormMatches = set()
        # if the defs have form matches, then those will necessarily lead to synonymOfForm matches, but we don't want to count these
        #print("trivialSynForm = {0}".format(trivialSynonymOfFormMatches))
        synonymOfForms1 = self.synonyms.at(self.forms1) #| self.forms1 # the forms are considered formsynonyms
        synonymOfForms2 = self.synonyms.at(self.forms2) #| self.forms2 
        
        synonymOfFormsIntersect = (synonymOfForms1 & self.forms2) | (synonymOfForms2 & self.forms1) |  (synonymOfForms1 & self.keywords2) | (synonymOfForms2 & self.keywords1)
        #print("form1 = {0}\nforms2 = {1}".format(self.forms1, self.forms2))
        #print("synform1 = {0}\nsynform2 = {1}".format(synonymOfForms1, synonymOfForms2))

        #print("synonymOfFormsIntersect = {0}".format(synonymOfFormsIntersect))
        #nonTrivialSynonymOfFormMatches = synonymOfFormsIntersect - trivialSynonymOfFormMatches
        #print("nontrivformsyn = {0}".format(nonTrivialSynonymOfFormMatches))
        self.addForNonEmpty(synonymOfFormsIntersect)


    def hyperonymMatch(self):
        synsets1 = self.synsets.at(self.keywords1)
        synsets2 = self.synsets.at(self.keywords2)

        #print("syns1 = {0}".format(synsets1))
        #print("syns2 = {0}".format(synsets2))
        hyperonyms1 = self.hyperonyms.at(synsets1)
        hyperonyms2 = self.hyperonyms.at(synsets2)

        #print("hyp1 = {0}".format(hyperonyms1))
        #print("hyp2 = {0}".format(hyperonyms2))
        hyperonyms1of2 = hyperonyms1 & synsets2
        hyperonyms2of1 = hyperonyms2 & synsets1

        #print(hyperonyms1of2)
        #print(hyperonyms2of1)

        if 8 in self.featureNumbersToUse:
            if hyperonyms1of2 or hyperonyms2of1:
                self.addFeature(1)
            else:
                self.addFeature(0)
        return synsets1, synsets2, hyperonyms1of2, hyperonyms2of1


    def formHyperonymMatch(self, synsets1, synsets2, hyperonyms1of2, hyperonyms2of1):
        formSynsets1 = self.synsets.at(self.forms1 | self.keywords1)
        formSynsets2 = self.synsets.at(self.forms2 | self.keywords2)

        formHyperonyms1 = self.hyperonyms.at(formSynsets1)
        formHyperonyms2 = self.hyperonyms.at(formSynsets2)

        formHyperonyms1of2 = (formHyperonyms1 & formSynsets2) | (formHyperonyms1 & synsets2) 
        formHyperonyms2of1 = (formHyperonyms2 & formSynsets1) | (formHyperonyms2 & synsets1) 

        nonTrivialFormHyperonyms1of2 = formHyperonyms1of2 - hyperonyms1of2 # decouple from hyperonymMatch feature
        nonTrivialFormHyperonyms2of1 = formHyperonyms2of1 - hyperonyms2of1

        if nonTrivialFormHyperonyms1of2 or nonTrivialFormHyperonyms2of1:
            self.addFeature(1)
        else:
            self.addFeature(0)



    def invertedNormalizedEditDistanceForm(self):
        formEditDistance = editdistance.eval(self.asjp1, self.asjp2) 
        normalizedEditDistance = float(formEditDistance) / self.maxLenWord
        invertedNormalizedEditDistance = 1 - normalizedEditDistance
        self.addFeature(invertedNormalizedEditDistance)


    def normalizedPrefix(self):
        prefixCount = 0
        for i in range(self.minLenWord):
            if self.asjp1[i] == self.asjp2[i]:
                prefixCount += 1
            else:
                break
        normalizedCommonPrefix = prefixCount / self.maxLenWord
        self.addFeature(normalizedCommonPrefix)

    def normalizedSuffix(self):
        suffixCount = 0
        for i in range(self.minLenWord):
            index = -1 * i - 1
            #print(index)
            if self.asjp1[index] == self.asjp2[index]:
                suffixCount += 1
            else:
                break
        #print("suffix count == {0}".format(suffixCount))
        normalizedCommonSuffix = suffixCount / self.maxLenWord
        self.addFeature(normalizedCommonSuffix)


    def alignmentFeatures(self):
        ''' add normalizedAlignedConsonants and ALINE score features '''
        if self.alignmentFeaturesDict is None:
            print("no alignment dict to look at")
            score, normalizedAlignedConsonants  = getAlignmentFeatures(self.aline1, self.aline2)
        else:
            score, normalizedAlignedConsonants = lookUpWordPairStrict(self.alignmentFeaturesDict, self.aline1, self.aline2)
            if score is None:
                sys.stderr.write("couldn't find pair: {0}, {1}\n".format(self.aline1, self.aline2))
                exit(-1)


        self.addFeature(normalizedAlignedConsonants)
        self.addFeature(score) # ALINE score as feature


    def normalizedLCSForm(self):
        ''' calculates the normalized longest common subsequence and adds it as a feature '''
        longestCommonSubsequence = StringSimilarity.lcs(self.asjp1, self.asjp2)
        normalizedLCS = float(len(longestCommonSubsequence)) / self.maxLenWord
        #print("normalizedLCS = {0}".format(normalizedLCS))
        self.addFeature(normalizedLCS)


    def word2VecFeatures(self):
        
        # split the defs on white spaces and semicolons to get a list of words to pass to the model
        # we are treating the whole thing as one big definition here. Even though
        # for other features we look at each split on semicolons

        maxAllWords = 0
        maxContentWords = 0
        for def1 in self.splitDefs1:
            words1 = def1.split()
            wordsInModel1 = [x for x in words1 if x in self.model]

            for def2 in self.splitDefs2:
                words2 = def2.split()
                wordsInModel2 = [x for x in words2 if x in self.model]

                #print("words in model1 = {0}".format(wordsInModel1))
                #print("words in model2 = {0}".format(wordsInModel2))
                scoreAllWords = self.getWord2VecScoreFromListsOfWords(wordsInModel1, wordsInModel2)
                #print("ScoreAllWords = {0}".format(scoreAllWords))
                if scoreAllWords > maxAllWords:
                    maxAllWords = scoreAllWords

                contentWordsInModel1 = [x for x in wordsInModel1 if x not in self.stopWords]
                contentWordsInModel2 = [x for x in wordsInModel2 if x not in self.stopWords]
                #print("content words in model1 = {0}".format(contentWordsInModel1))
                #print("content words in model2 = {0}".format(contentWordsInModel2))

                scoreContentWords = self.getWord2VecScoreFromListsOfWords(contentWordsInModel1, contentWordsInModel2)
                #print("scoreContentWords = {0}".format(scoreContentWords))
                if scoreContentWords > maxContentWords:
                    maxContentWords = scoreContentWords
        
        self.addFeature(maxAllWords)
        self.addFeature(maxContentWords)

        # we filter the words based on whether they asre in the model or not
        # otherwise we would get a key error
        

    def getWord2VecScoreFromListsOfWords(self, words1, words2):
        if words1 == [] or words2 == []:
            # at least one of the sentences has no words in the model so simply return 0
            score = 0.0
        else:
            # the score from the model on each list of words
            score = self.model.n_similarity(words1, words2)
        return score









