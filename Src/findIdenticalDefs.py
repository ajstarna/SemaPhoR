#!/usr/bin/env python3

''' this file will read in the language dictionaries and partition them into sets with identical definitions and print these same definition sets '''


from LanguageDictParser import AlgonquianLanguageDictParser
import DefinitionCleaner
from UniToASJPConverter import uniToASJP

from CogSetFileReader import CogSetFileReader

from collections import defaultdict
import time
import sys


class IdenticalDefFinder(object):

    def __init__(self, languageFamily, printDefinition, displayASJP, uniAndASJP, firstLetter, sameDefsFile, nonSameDefsFile):
        self.languageFamily = languageFamily
        self.printDefinition = printDefinition # flag bool indicates if we print sets with definition or not
        self.displayASJP = displayASJP # bool flag indicates if words should be displayed in asjp instead of as unicode
        self.uniAndASJP = uniAndASJP # bool flag indicates if words should be displayed in both unicode and asjp
        self.firstLetter = firstLetter # flag to either print sets partitioned by same first letter or not

        # open the files to overwrite anything already there
        self.sameDefsFile = open(sameDefsFile, 'w')

        if not nonSameDefsFile is None:
            self.nonSameDefsFile =  open(nonSameDefsFile, 'w')
        else:
            self.nonSameDefsFile = None



    def findAndPrintSets(self):
        ''' main method to call to find all such sets and print them out '''

        if self.languageFamily == "totonac":
            self.readTotonacGold()

        self.findSets()

        self.printSets()
        self.sameDefsFile.close()

        if not self.nonSameDefsFile is None:
            self.printNonSameDefWords()
            self.nonSameDefsFile.close()

        print("same def words = {0}".format(len(self.allWordsInASet)))
        print("non same def words = {0}".format(len(self.nonSameDefWords)))
              
        
    def findSets(self):
        ''' method for finding the sets with identical definitions. Populates a dictionary mapping cleaned and split defintions to
        all words with this definition'''

        self.ldp = self.parseLanguageFiles() # read in the dictionaries
        self.definitionToWords = defaultdict(set) # this dicitonary maps a definition to a list of words with this definition
        self.wordTupleToUni = {}

        self.allWordsInASet = defaultdict(int) # keeps track of words in a set, want to see if a word makes it into multiple sets
        for langAcc in self.ldp.getLangs():
            langDict = self.ldp[langAcc]
            for word in langDict:
                definitions = langDict[word]

                self.currentUniWord = word
                self.currentASJPWord = uniToASJP(word)
                for defn in definitions:
                    wordTuple = (langAcc, word, defn)
                    self.cleanAndAddDefn(defn, langAcc)



    def cleanAndAddDefn(self, defn, langAcc):
        cleanedDefs = DefinitionCleaner.definitionCleanAndSplit(defn)
        for cleanDef in cleanedDefs:
            self.updateDefinitionToWords(cleanDef, langAcc, defn)

    def updateDefinitionToWords(self, cleanDef, langAcc, defn):
        toAdd = (langAcc, self.currentASJPWord, self.currentUniWord, defn)
        self.definitionToWords[cleanDef].add(toAdd)


    def printSet(self, defn, wordsWithSameDef):
        ''' this method only prints the given definition if the printDefinition flag was set to True. '''
        if self.printDefinition:
            self.sameDefsFile.write(defn + "\n")

        for wordTuple in sorted(wordsWithSameDef): # sort by language and then word form (default order of tuple)
            self.allWordsInASet[wordTuple] += 1
            printTuple = self.getPrintTuple(wordTuple)
            self.sameDefsFile.write("\t".join(printTuple) + "\n")
        self.sameDefsFile.write("\n")


    def getPrintTuple(self, wordTuple):
        if self.uniAndASJP:
            return wordTuple

        acc, asjp, uni, defn = wordTuple
        if self.displayASJP:
            word = asjp
        else:
            word = uni
        if self.printDefinition:
            printTuple = (acc, word, defn)
        else:
            printTuple = (acc, word)
        return printTuple


    def printSetFirstLetters(self, defn, wordsWithSameDef):
        ''' given a set of wordtuples with the same definition, prints out the sets in groups with same first letter '''

        letterToWords = defaultdict(list)
        for wordTuple in wordsWithSameDef:
            word = wordTuple[1]
            firstLetter = word[0]
            letterToWords[firstLetter].append(wordTuple)

        for firstLetter in sorted(letterToWords):
            currentWordTuples = letterToWords[firstLetter]
            if len(currentWordTuples) > 1 and not self.onlyOneLanguageSet(currentWordTuples):
                # now that the set has been paritioned into subsets with the same first letter, we
                # must reconfirm that the subset also has multiple words and not all from the same language
                self.printSet(defn, currentWordTuples)
            else:
                self.addToNonSameDefWords(currentWordTuples) 


    def printSets(self):
        ''' prints out each set with identical definitions. Must be called after findSets() '''
        self.nonSameDefWords = set()
        for defn in sorted(self.definitionToWords):
            wordsWithSameDef = self.definitionToWords[defn]
            if len(wordsWithSameDef) > 1 and not self.onlyOneLanguageSet(wordsWithSameDef):
                    if self.firstLetter:
                        self.printSetFirstLetters(defn, wordsWithSameDef)
                    else:
                        self.printSet(defn, wordsWithSameDef)
            else:
                self.addToNonSameDefWords(wordsWithSameDef) 


    def addToNonSameDefWords(self, wordTuples):
        for wordTuple in wordTuples:
            self.nonSameDefWords.add(wordTuple)

    def printNonSameDefWords(self):
        for wordTuple in sorted(self.nonSameDefWords, key=lambda x: (x[1],x[2],x[0],x[3])): # sort by asjp, then uni, then lang, then defn
            self.nonSameDefsFile.write("\t".join(wordTuple) + "\n")


    def onlyOneLanguageSet(self, wordSet):
        ''' given a set of word tuples, determines if the set contains words from only one language or not '''
        return False # Feb 9-17 (does this function actually matter???)
        languages = set()
        for wordTuple in wordSet:
            acc = wordTuple[0]
            languages.add(acc)
        if len(languages) < 2:
            # only one acc in the languages set, so return True, i.e only one language in set
            return True
        else:
            return False

    def parseLanguageFiles(self):
        if self.languageFamily == "algonquian":
            ldp = AlgonquianLanguageDictParser()
        else:
            sys.stderr.write("unknown language family!\n")
            exit(-1)
        return ldp

    def printWordsInMultipleSets(self):
        # for debugging...
        print("MULTISETWORDS")
        numMultiSet = 0
        numSingleSet = 0
        for wordTuple in sorted(self.allWordsInASet, key=lambda x: x[1]): # sorted by form
            count = self.allWordsInASet[wordTuple]
            if count > 1:
                print("\t".join(wordTuple))
                numMultiSet += 1
            else:
                numSingleSet += 1
        print("number of multi set words = {0}".format(numMultiSet))
        print("number of single set words = {0}".format(numSingleSet))
            




class StrictIdenticalDefFinder(IdenticalDefFinder):
    ''' this class is more strict than the identical def finder. It only considers definitions identical in the entire gloss,
    whereas the IdenticalDefFinder class will consider sub-definitions, ones that are split on comma.
    e.g. IdenticalDefFinder could put a word with gloss "day, sky" into two sets, one for "day" and one for "sky"
    this class would only put that word into a set with full gloss "day, sky"
    '''

    def cleanAndAddDefn(self, defn, langAcc):
        cleanedDef = DefinitionCleaner.cleanDef(defn) # here we only consider the entire cleaned definition
        if cleanedDef == "":
            return
        self.updateDefinitionToWords(cleanedDef, langAcc, defn)




if __name__ == "__main__":

    import optparse

    parser = optparse.OptionParser()
    parser.add_option('-l', action='store', dest='languageFamily', help="the language family. default = algonquian", default="algonquian")
    parser.add_option('-f', action='store_true', dest='firstLetter', help="use flag if want sets with same first letter.", default=False)
    parser.add_option('-d', action='store_true', dest='definition', help="use flag if want sets to include definition", default=False)
    parser.add_option('-a', action='store_true', dest='asjp', help="use flag if want words in asjp representation instead of unicode", default=False)
    parser.add_option('-b', '--uniAndASJP', action='store_true', dest='uniAndASJP', help="use flag if want words in unicode and asj asjp", default=False)

    parser.add_option('-s', action='store', dest='sameDefFile', help="name of file to write same def sets to")
    parser.add_option('-n', action='store', dest='nonSameDefFile', help="file name to print out non same def words", default=None)

    parser.add_option('-t', action='store_true', dest='strictSets', help="use flag if want to only consider sets a same definition if the entire clean gloss matches.")


    parser.add_option('-m', action='store_true', dest='printMultiSetWords', help="use flag if want to print words in multiple sets at the end of file for debugging.", default=False)



    options, args = parser.parse_args()


    if options.languageFamily in ["algonquian", "totonac"]:
        pass
    else:
        sys.stderr.write("Unknown language family!\n")
        parser.print_help()
        exit(-1)



    t1 = time.clock()

    if options.strictSets:
        sys.stderr.write("Strict sets!\n")
        finder = StrictIdenticalDefFinder(options.languageFamily, options.definition, options.asjp, options.uniAndASJP, options.firstLetter, 
                                          options.sameDefFile, options.nonSameDefFile)
    else:
        finder = IdenticalDefFinder(options.languageFamily, options.definition, options.asjp, options.uniAndASJP, options.firstLetter, 
                                    options.sameDefFile, options.nonSameDefFile)

    finder.findAndPrintSets()


    if options.printMultiSetWords:
        finder.printWordsInMultipleSets()


    t2 = time.clock()
    seconds = t2- t1
    minutes = seconds/60.0
    hours = minutes/60.0
    sys.stderr.write("Time to run was {0}s = {1}m = {2}h\n".format(seconds, minutes, hours))


