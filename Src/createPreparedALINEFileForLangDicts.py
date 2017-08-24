#!/usr/bin/env python3

''' this file reads from two languages and calculates alignment features (nusimil score and # aligned consonants) for each possible pair between them.
they are written to a binary file with a given output name

example run:
./createAlignmentFeaturesForLangDicts.py --l1 C --l2 M -o alignmentFeaturesCreeMeno.bin

'''

import sys
import time

from PreparedFileCreator import ALINEFileCreator
from LanguageDictParser import LanguageDictParser

class LangDictsALINEFileCreator(ALINEFileCreator):

    def __init__ (self, acc1, acc2, langFile1, langFile2, definitionLanguage, outputName):
        super().__init__(outputName)
        self.acc1 = acc1
        self.acc2 = acc2
        self.langFile1 = langFile1
        self.langFile2 = langFile2
        self.definitionLanguage = definitionLanguage


    def createALINEFile(self):
        ldp = LanguageDictParser([self.acc1, self.acc2], [self.langFile1, self.langFile2], self.definitionLanguage)
        self.langDicts = ldp.parseAllFiles()

        sys.stderr.write("looking at {0} and {1}\n".format(self.langFile1, self.langFile2))
        sys.stderr.write("size of dict1 = {0}\n".format(len(self.langDicts[self.acc1])))
        sys.stderr.write("size of dict2 = {0}\n\n".format(len(self.langDicts[self.acc2])))

        t1 = time.time()
        countOuter = 0

        dict1 = self.langDicts[self.acc1]
        dict2 = self.langDicts[self.acc2]
        words1 = list(dict1.keys())
        words1.sort()
        words2 = list(dict2.keys())
        words2.sort()

        startIndex = 0
        for i, word1 in enumerate(words1):
            countOuter += 1
            t2 = time.time()
            seconds = t2- t1
            minutes = seconds/60.0
            hours = minutes/60.0
            sys.stderr.write("\033[F")
            sys.stderr.write("{0} / {1}  dict1 words looked at; Time so far is {2:.2f}s = {3:.2f}m = {4:.2f}h\n".format(i, len(words1), seconds, minutes, hours))

            aline1 = self.getALINE(word1)
            if self.acc1 == self.acc2:
                startIndex = i + 1
            for j in range(startIndex, len(words2)):
                word2 = words2[j]
                aline2 = self.getALINE(word2)
                self.writeToFile(aline1, aline2)

    

if __name__ == "__main__":

    import optparse
    
    parser = optparse.OptionParser()
    parser.add_option('-o', action='store', dest='outputName', help="the output file.")
    parser.add_option('--l1', action='store', dest='acc1', help="the language Acc for first language (ex. C,F,M,O)")
    parser.add_option('--l2', action='store', dest='acc2', help="the language Acc for second language (ex. C,F,M,O)")
    parser.add_option('--lang', action='store', dest='language', help="the language of the definitions in the example pairs. default = en", default="en")

    options, args = parser.parse_args()

    accToLangFile = dict([("C", "cree.xml"), ("F", "fox.xml"), ("M", "meno.xml"), ("O", "oji.xml")])

    if options.outputName is None:
        sys.stderr.write("Must provide the output name!\n")
        exit(-1)
        

    if options.acc1 is None or options.acc2 is None:
        sys.stderr.write("Must provide the language accronyms!\n")
        exit(-1)


    langFile1 = accToLangFile[options.acc1]
    langFile2 = accToLangFile[options.acc2]


    t1 = time.time()
    with LangDictsALINEFileCreator(options.acc1, options.acc2, langFile1, langFile2, options.language, options.outputName) as creator:
        creator.createALINEFile()
    t2 = time.time()
    seconds = t2- t1
    minutes = seconds/60.0
    hours = minutes/60.0
    sys.stderr.write("Time to run was {0:.2f}s = {1:.2f}m = {2:.2f}h\n".format(seconds, minutes, hours))
