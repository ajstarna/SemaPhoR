#!/usr/bin/env python3

''' this module will contain the classes and methods needed to take words and definition pairs and create SVM feature values
    see runSubstringFeaturizer.py for an example of using these classes
'''


import StringSimilarity
from collections import OrderedDict


class Featurizer(object):
    ''' base class for featurizing. Has methods for initializing and printing outputs. '''

    def __init__(self, maxSubstringLength, training, substitutionCost=2):
        # training bool indicates if training, or False if testing. The difference is in the way that features are added
        # if training then creates the feature dict and writes to file, if testing then reads it
        self.maxSubstringLength = maxSubstringLength
        self.substitutionCost = substitutionCost # for the levenshtein algorithm, Bergsma-Kondrak use 2
        self.featureDict = OrderedDict()
        self.training = training
        if not training:
            self.testingOnlyFeatures = set() # keep track of features that appear in testing that are not part of the feature dict
            self.seenTrainingFeatures = set() # keep track of features seen in testing that were also in training
            self.allTestingFeatures = set()


    def setWords(self, word1, word2, classification=-1):
        # give the featurizer the 2 words we currently looking at and the classification (-1 or +1)
        self.word1 = self.addBoundaryChars(word1)  # add boundary characters at start and end of words
        self.word2 = self.addBoundaryChars(word2)

        #self.word1 = word1 # April 11-17 removing boundary characters to attempt to remove first character bias
        #self.word2 = word2 # this didn't work

        self.classification = classification
        self.alignment = StringSimilarity.leven_with_alignment(self.word1, self.word2, self.substitutionCost)[1] # don't need the score so just grab alignment
        #print(self.alignment)
        #top = ""
        #bottom = ""
        #for pair in self.alignment:
        #    top += pair[0]
        #    bottom += pair[1]
        #print(top)
        #print(bottom)
        self.currentFeatures = OrderedDict()
        self.currentFeatureNumMapping = {}
        self.createAlignmentDicts()
        self.createAllSubstrings()


    def createAlignmentDicts(self):
        # the aligment dicts map an index in one word to the index in the other word that the character is mapped to in
        # the alignment. If the character at the index is not aligned, then the dict maps to None
        self.leftToRight = {}
        self.rightToLeft = {}

        leftPosition = 0
        rightPosition = 0
        
        # goes through the alignment. When a "-" appears on either side, this means that the char for the other word
        # is aligned to "-", i.e. not aligned
        # the Position keeps track of the actual index in the word, so when a "-" appears for a side, then that Position
        # is not incremented since we didn't actually see a character
        for leftChar, rightChar in  self.alignment:
            #print(leftChar, rightChar)
            if leftChar == "-":
                self.rightToLeft[rightPosition] = None
                rightPosition += 1
            elif rightChar == "-":
                self.leftToRight[leftPosition] = None
                leftPosition += 1
            else:
                self.leftToRight[leftPosition] = rightPosition
                self.rightToLeft[rightPosition] = leftPosition
                rightPosition += 1
                leftPosition += 1



    def createAllSubstrings(self):
        # creates all substrings for each word
        self.leftSubstringsWithIndices = self.createSubstringsForWord(self.word1)
        self.rightSubstringsWithIndices = self.createSubstringsForWord(self.word2)


    def createSubstringsForWord(self, word):
        # creates all substring tuples for a given word
        # the substring tuple is the substring itself, plus the starting and ending indices
        substrings = []
        for i in range(len(word)):
            substring = ""
            j = 0
            while j < len(word) - i:
                i2 = i + j
                char = word[i2]
                substring += char
                addition = (substring, i, i2) 
                substrings.append(addition)
                j += 1

        return substrings



    def addPhraseFeatures(self):
        for leftSubstringTuple in self.leftSubstringsWithIndices:
            for rightSubstringTuple in self.rightSubstringsWithIndices:
                if self.areConsistent(leftSubstringTuple, rightSubstringTuple):
                    # only add substring that are consistent with the alignment
                    feature = leftSubstringTuple[0] + " " + rightSubstringTuple[0] # phrase features separated by a space
                    self.addFeature(feature)



    def areConsistent(self, leftSubstringTuple, rightSubstringTuple):
        # returns true or false if a pair of substring tuples is consistent with the alignment
        leftSubstring, leftStart, leftEnd = leftSubstringTuple
        rightSubstring, rightStart, rightEnd = rightSubstringTuple

        notAllNone = False # this just keeps track that there is at least one alignment as part of the substrings
        # we don't want a substring pair of ALL unaligned characters to be a feature


        if leftEnd - leftStart >= self.maxSubstringLength or rightEnd - rightStart >= self.maxSubstringLength:
            return False


        for leftPosition in range(leftStart, leftEnd+1):
            leftAlign = self.leftToRight[leftPosition]
            if not (leftAlign is None):
                notAllNone = True
                if not (leftAlign in range(rightStart, rightEnd+1)):
                    return False

        for rightPosition in range(rightStart, rightEnd+1):
            rightAlign = self.rightToLeft[rightPosition]
            if not (rightAlign is None):
                notAllNone = True
                if not (rightAlign in range(leftStart, leftEnd+1)):
                    return False
        if notAllNone:
            return True
        else:
            return False
          



    def addMismatchFeaturesWithAlignmentChars(self):
        # create mismatch features to match Shane's code. Where "-" characters from the alignment are part of the feature
        # my original way of implementing does not include the "-" characters as part of the feature. 
        # testing both ways and end up giving identical predictions, so sticking with this way since it runs quicker
        self.mismatchFeatures = []
        for i, alignTuple in enumerate(self.alignment):
            #print(i, alignTuple)
            leftChar, rightChar = alignTuple

            if leftChar == rightChar:
                # start looking for a mismatch if the first chars are aligned
                leftSide = leftChar
                rightSide = rightChar

            else:
                continue


            # now that we have an aligned starting point, go through the next characters until we find another aligned pair
            # needs to be at least one unaligned char in between
            j = i+1
            while j < len(self.alignment):
                nextTuple = self.alignment[j]
                leftNext, rightNext = nextTuple
                leftSide += leftNext
                rightSide += rightNext
                if leftNext == rightNext:
                    # found the end of this mismatch
                    if len(leftSide) != 2:
                        # Don't want a feature that is simply 2 aligned chars to 2 aligned chars, so length must be greater than 2
                        contextFeature = leftSide + ":" + rightSide
                        self.addFeature(contextFeature)
                        self.mismatchFeatures.append(contextFeature)

                        noContextFeature = leftSide[1:-1] + "::" + rightSide[1:-1] # without context: we get rid of the first and last char from each, i.e. the aligned chars
                        self.addFeature(noContextFeature)
                        self.mismatchFeatures.append(noContextFeature)
                    break
                j+= 1


                '''
    def addMismatchFeatures(self):
        # look through all substrings and add those which are deemed to be a "mismatch" feature
        for leftSubstringTuple in self.leftSubstringsWithIndices:
            for rightSubstringTuple in self.rightSubstringsWithIndices:
                if self.areMismatch(leftSubstringTuple, rightSubstringTuple):
                    # only add substring that are mismatches
                    contextFeature = leftSubstringTuple[0] + "::" + rightSubstringTuple[0]
                    self.addFeature(contextFeature)
                    noContextFeature = leftSubstringTuple[0][1:-1] + ":" + rightSubstringTuple[0][1:-1]
                    self.addFeature(noContextFeature)
                    '''

    def areMismatch(self, leftSubstringTuple, rightSubstringTuple):
        leftSubstring, leftStart, leftEnd = leftSubstringTuple
        rightSubstring, rightStart, rightEnd = rightSubstringTuple

        # if the end points don't align to each other, then cannot be a mismatch feature
        if self.leftToRight[leftStart] != rightStart or self.leftToRight[leftEnd] != rightEnd:
            return False

        # now that we know that the ends are aligned, we must verify that all internal charcters are not aligned to anything
        # and we need that there exists at least one unaligned char in between. Don't want a feature that is simply 2 aligned chars to 2 aligned chars
        atLeastOneUnaligned = False
        for leftPosition in range(leftStart+1, leftEnd):
            leftAlign = self.leftToRight[leftPosition]
            if (not leftAlign is None):
                return False
            atLeastOneUnaligned = True

        for rightPosition in range(rightStart+1, rightEnd):
            rightAlign = self.rightToLeft[rightPosition]
            if (not rightAlign is None):
                return False
            atLeastOneUnaligned = True

        if atLeastOneUnaligned:
            return True
        else:
            return False




    def addFeature(self, substring):
        ''' sets the feature for the given substring. '''
        if self.training:
            self.addFeatureTraining(substring)
        else:
            self.addFeatureTesting(substring)


    def addFeatureTraining(self, substring):
        if substring in self.featureDict:
            featureNum = self.featureDict[substring]
        else:
            # a new feature for the feature dict, assign it a new number
            featureNum = len(self.featureDict) + 1
            self.featureDict[substring] = featureNum

        if substring in self.currentFeatures:
            # currentFeatures keeps track of how many times a feature has been seen
            self.currentFeatures[substring] += 1 
        else:
            self.currentFeatures[substring] = 1 
            self.currentFeatureNumMapping[featureNum] = substring 



    def addFeatureTesting(self, substring):
        self.allTestingFeatures.add(substring)
        if substring in self.featureDict:
            featureNum = self.featureDict[substring]
            self.seenTrainingFeatures.add(featureNum)
        else:
            self.testingOnlyFeatures.add(substring)
            return
        
        if substring in self.currentFeatures:
            # currentFeatures keeps track of how many times a feature has been seen
            self.currentFeatures[substring] += 1 
        else:
            # first time seeing a feature, set count to 1
            self.currentFeatures[substring] = 1 
            self.currentFeatureNumMapping[featureNum] = substring 


    def printTestingOnlyFeatures(self):
        print("TESTING ONLY FEATURES")
        for substring in self.testingOnlyFeatures:
            print(substring)


    def addBoundaryChars(self, word):
        return "^" + word + "$"


    def featurizeGivenPair(self, word1, word2, classification=-1):
        self.setWords(word1, word2, classification)
        self.addPhraseFeatures()
        self.addMismatchFeaturesWithAlignmentChars()



    def featurizeAndWrite(self,  word1, word2, classification=-1, outputFile=None):
        self.setWords(word1, word2, classification)
        self.addPhraseFeatures()
        self.addMismatchFeaturesWithAlignmentChars() # this way uses alignment chars but can change if want to other method
        #self.addMismatchFeatures() 
        self.writeFeatures(outputFile) # method to be implemented by inherited classes



    def writeFeatureDictToFile(self, featureDictFileName):
        # each line of the feature dict file is the feature, then a tab, then the feature number
        with open(featureDictFileName, 'w') as file:
            for substring in self.featureDict:
                featureNum = self.featureDict[substring]
                file.write(substring + "\t" + str(featureNum) + "\n")


    def readFeatureDictFromFile(self, featureDictFileName):
        self.featureDict = OrderedDict()
        with open(featureDictFileName, 'r') as file:
            for line in file:
                line = line.strip()
                substring, featureNum = line.split('\t')
                self.featureDict[substring] = int(featureNum)


    def printAlignedWords(self):
        # for debugging
        word1Align = ""
        word2Align = ""
        for leftChar, rightChar in self.alignment:
            word1Align += leftChar
            word2Align += rightChar

        print(word1Align)
        print(word2Align)


class FeaturizerForShaneOutput(Featurizer):
    # this class will print out a current feature dict in the format to compare against Shane's phrasal output
    # the line has each feature delimited by "|" characters and with a "|" at the end of the line
    # other method for printing out just the mismatch features

    def  __init__(self, maxSubstringLength, training=True, substitutionCost=2):
        super().__init__(maxSubstringLength, substitutionCost)


    def printPhrasesLine(self, outputFile=None):
        result = ""
        for feature in self.currentFeatures:
            for i in range(self.currentFeatures[feature]):
                result += feature + "|"
        if outputFile is None:
            print(result)
        else:
            outputFile.write(result+'\n')


    def printMismatches(self):
        for feature in self.mismatchFeatures:
            print(feature)
            if outputFile is None:
                print(feature)
            else:
                outputFile.write(feature)

        if outputFile is None:
            print()
        else:
            outputFile.write('\n')

    


class SubstringFeaturizerForSVMLight(Featurizer):
    ''' this class inherits the featurizer class to create phrase and mismatch substring features.
    It contains methods for printng out the results in a way readable to svm-light '''


    def  __init__(self, maxSubstringLength, training=True, substitutionCost=2):
        super().__init__(maxSubstringLength, training, substitutionCost)



    def getOutputLine(self=None):
        ''' creates the string of SVM features and prints '''
        outputLine = str(self.classification)
        for featureNum in sorted(self.currentFeatureNumMapping):
            substring = self.currentFeatureNumMapping[featureNum]
            featureValue = self.currentFeatures[substring]
            outputLine += " " + str(featureNum) + ":"
            outputLine += str(featureValue)
        return outputLine


    def writeFeatures(self, outputFile=None):
        outputline = self.getOutputLine
        if outputFile is None:
            print(outputLine)
        else:
            outputFile.write(outputLine+'\n')






