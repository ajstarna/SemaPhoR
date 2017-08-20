#!/usr/bin/env python3


''' example use: ./createAlignmentFeatures.py -o cree_fox_alignmentFeatures.txt --l1 C --l2 F 
reads the dictionaries of the given files and creates the alignment and aligned consonants scores for each pairwise word pair from the two languages.
writes them to a file so these features can simply be looked up when creating svm features. the nusimil program needs to be run, so this would be the 
bottle neck if doing this featurization on the fly.'''

import sys
sys.path.insert(0,'../Utils')

import time
import struct


from UniToALINEConverter import uniToALINE
from ASJPToALINEConverter import asjpToALINE
import binaryReadAndWrite

vowels = set('aeiou3EOI')

nonCons = vowels | {"-", "|"} # non consonants


def getAlignmentFeatures(s1, s2):
    lines = Nusimil.nusimil(s1, s2)
    return getAlignmentFeaturesFromNusimilOutput(lines)

def getAlignmentFeaturesFromNusimilOutput(lines):
    try:
        score = float(lines[0])
    except:
        print("problem with {0}".format(lines))
        print(lines)
        exit(-1)

    firstAlignment = lines[1].split()
    secondAlignment = lines[2].split()
    #print(firstAlignment)
    #print(secondAlignment)
    normalizedAlignedCons = alignedConsonants(firstAlignment, secondAlignment)
    return score, normalizedAlignedCons


def alignedConsonants(letters1, letters2):
    # returns the number of aligned consonants divided by the maximum number of consonants in either word
    alignedCons = 0
    cons1 = 0
    cons2 = 0

    for i, l in enumerate(letters1):
        letter1 = letters1[i][0] # just want the first letter if there is two, e.g. aH in ALINE
        letter2 = letters2[i][0]
        if not letter1 in nonCons: #vowels and letter1 != "-" and letter1 != "|":
            # letter1 a cons
            cons1 += 1
            currentCons1 = True
        else:
            currentCons1 = False

        if not letter2 in nonCons: #vowels and letter2 != "-" and letter2 != "|":
            cons2 += 1
            if currentCons1:
                # both a consonant
                alignedCons += 1

    maxCons = max(cons1, cons2, 1) # add the 1 so we don't divide by 0  by accident if no consonants in either

    normalizedAlignedCons = float(alignedCons) / maxCons

    return normalizedAlignedCons




def lookUpWordPair(scoresDict, aline1, aline2):
    ''' given a alignment score dictionary read from a file, and two aline words, it looks up their
    score in the dictionary. If they are not present in the dictionary, computes their scores from scratch '''

    bytes1 = bytes(aline1, "ASCII")
    bytes2 = bytes(aline2, "ASCII")
    wordTuple1 = (bytes1, bytes2)
    wordTuple2 = (bytes2, bytes1) # can't be sure what order they are in (unless we look at accs? TODO?)

    if scoresDict is None:
        score, normalizedAlignedConsonants  = getAlignmentFeatures(aline1, aline2) 
    elif wordTuple1 in scoresDict:
        score, normalizedAlignedConsonants = scoresDict[wordTuple1]
    elif wordTuple2 in scoresDict:
        score, normalizedAlignedConsonants = scoresDict[wordTuple2]
    else:
        score, normalizedAlignedConsonants  = getAlignmentFeatures(aline1, aline2) # they not in the dict somehow; shouldnt happen

    return score, normalizedAlignedConsonants


def lookUpWordPairStrict(scoresDict, aline1, aline2):
    ''' given a alignment score dictionary read from a file, and two aline words, it looks up their
    score in the dictionary. If they are not present in the dictionary, returns None for both scores '''

    if scoresDict is None:
        return None, None

    bytes1 = bytes(aline1, "ASCII")
    bytes2 = bytes(aline2, "ASCII")
    wordTuple1 = (bytes1, bytes2)
    wordTuple2 = (bytes2, bytes1) # can't be sure what order they are in (unless we look at accs? TODO?)

    if wordTuple1 in scoresDict:
        score, normalizedAlignedConsonants = scoresDict[wordTuple1]
    elif wordTuple2 in scoresDict:
        score, normalizedAlignedConsonants = scoresDict[wordTuple2]
    else:
        score, normalizedAlignedConsonants  =  None, None

    return score, normalizedAlignedConsonants



class AlignmentFeatureValuesWriter(object):
    ''' this class will write the alignment features to file. Inherited by other classes which decide where the pairs come from '''

    def __init__(self, outputFileName):
        self.outputFileName = outputFileName
        # open the file just to overwrite them to nothing, since we will be appending to them,
        # and don't want to append to a previous run of the code
        with open(self.outputFileName, 'w') as file:
            pass

        self.uni2ALINEDict = {}
        self.scoreStruct = struct.Struct('f') # used to convert float values to binary for writing to file
        self.lengthStruct = struct.Struct('H') # used to convert the length integer to binary for writing to file
    

    # the enter and exit methods are definied to automatically open and close the output file                                                                                                              
    # these methods get called when executing a Python "with" statement 
    def __enter__(self):
        self.outputFile = open(self.outputFileName, "ba")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.writeFinalBytes()
        self.outputFile.close()


    def getALINE(self, uni):
        if uni in self.uni2ALINEDict:
            return self.uni2ALINEDict[uni]
        else:
            aline = uniToALINE(uni)
            aline = aline.replace("L", "") # added Jan 19. get rid of L since it is basically meaningless and it is messing up nusimil
            self.uni2ALINEDict[uni] = aline
            return aline


    def getAlignmentFeatures(self, s1, s2):
        return getAlignmentFeatures(s1, s2)

    def getAlignmentFeaturesFromNusimilOutput(self, lines):
        return getAlignmentFeaturesFromNusimilOutput(lines)


    def writeToFile(self, word1, word2, aline1, aline2, score, normalizedAlignedCons):
        #with open(self.outputName, "a") as file:
        self.outputFile.write("\t".join((word1, word2, aline1, aline2, str(score), str(normalizedAlignedCons))) + "\n")


    def writeToBinaryFile(self, aline1, aline2, alineScore, consScore):
        binaryReadAndWrite.writeToBinary(self.outputFile, aline1, aline2, alineScore, consScore, self.scoreStruct, self.lengthStruct)


    def writeFinalBytes(self):
        binaryReadAndWrite.writeFinalBytes(self.outputFile, self.lengthStruct)
