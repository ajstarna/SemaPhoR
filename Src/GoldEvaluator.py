
from collections import defaultdict
from CogSetFileReader import CogSetFileReader

import DefinitionCleaner

class GoldEvaluator(object):

    def __init__(self, cogSetFile):
        self.cogSetFile = cogSetFile
        self.numToCognateSet, self.wordToCogNum  = self.createGoldDicts()


    def createGoldDicts(self):
        ''' this method goes through the complete numToCognateSet dictionary, and for every word tuple, adds that tuple to the 
        created dictionary, mapping word tuple to cognate numbers. i.e. creates the inverse dictionary '''
        self.dirtyNumToCognateSet =  CogSetFileReader(self.cogSetFile).getNumToCognateSet()

        wordToCogNum = dict() #defaultdict(list)
        numToCogSet = defaultdict(list)
        
        self.dirtyWordToCogNum = dict()

        for num in sorted(self.dirtyNumToCognateSet):
            for wordTuple in self.dirtyNumToCognateSet[num]:
                cleanTuple = self.cleanTuple(wordTuple) # gold data is stored with definition cleaned
                wordToCogNum[cleanTuple] = num
                self.dirtyWordToCogNum[wordTuple] = num
                numToCogSet[num].append(cleanTuple)
        return numToCogSet, wordToCogNum


    def cleanTuple(self, wordTuple):
        ''' given a word tuple (acc, word, defn) with a possible unclean definition (may already be clean which is fine), this method
        returns a new tuple with the definition being cleaned '''
        acc, word, defn = wordTuple
        cleanDefn = DefinitionCleaner.cleanDef(defn)
        cleanTuple = (acc, word, cleanDefn)
        return cleanTuple


    def areCognates(self, wordTuple1, wordTuple2):
        ''' method to check if two words are cognate accordining to the gold file.
        If the cleaned version of the word tuples are identical, then they are considerred cognate whether or not in gold dict
        else:
        If either word is not in the dictionary, then this is automatically False.
        words are represented as (accronym, word, defn)'''


        if wordTuple1 == wordTuple2:
            return True

        cleanTuple1 = self.cleanTuple(wordTuple1)
        cleanTuple2 = self.cleanTuple(wordTuple2)


        if (not self.inGold(cleanTuple1)  or (not self.inGold(cleanTuple2))):
            # if either not in gold then cannot be cognate 
            return False

        return self.getCogNum(cleanTuple1) == self.getCogNum(cleanTuple2)


    def areCognatesDirty(self, wordTuple1, wordTuple2):
        ''' method to check if two words are cognate accordining to the gold file.
        Here, non-cleaned versions are checked
        If either word is not in the dictionary, then this is automatically False.
        words are represented as (accronym, word, defn)'''


        if wordTuple1 == wordTuple2:
            return True

        if (wordTuple1 not in self.dirtyWordToCogNum or wordTuple2 not in self.dirtyWordToCogNum):
            # if either not in gold then cannot be cognate 
            return False

        return self.dirtyWordToCogNum[wordTuple1] == self.dirtyWordToCogNum[wordTuple2]


    def getCogNum(self, cleanTuple):
        ''' method to get the cog num from a word tuple. Note: it is assumed that the tuple is already cleaned
        and that it is known to exist in the gold '''
        return self.wordToCogNum[cleanTuple]

    def getCogNumFromTuple(self, wordTuple):
        cleanTuple = self.cleanTuple(wordTuple)
        if self.inGold(cleanTuple):
            cogNum = self.getCogNum(cleanTuple)
            return cogNum
        else:
            return None


    def getCogSetFromCogNum(self, cogNum):
        '''given a cog num which is known to be in the gold, returns the cogSet '''
        return self.numToCognateSet[cogNum]

    def getDirtyCogSetFromCogNum(self, cogNum):
        '''given a cog num which is known to be in the gold, returns the cogSet '''
        return self.dirtyNumToCognateSet[cogNum]


    def inGold(self, cleanTuple):
        ''' method to check if a word tuple is in the gold. Note: it is assumed that the tuple is already cleaned '''
        return cleanTuple in self.wordToCogNum


    def getCogSetFromTuple(self, wordTuple):
        ''' given a wordTuple, returns the cognate set to which it belongs, or None if not part of a cognate set '''
        cleanTuple = self.cleanTuple(wordTuple)
        if self.inGold(cleanTuple):
            cogNum = self.getCogNum(cleanTuple)
            cogSet = self.getCogSetFromCogNum(cogNum)
            return cogSet
        else:
            return None
