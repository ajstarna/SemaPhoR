#!/usr/bin/env python3

# testing writing and reading to a binary file, for alignment score features


from struct import Struct

import sys

def writeToBinary(fileHandle, word1, word2, alineScore, consScore, scoreStruct, lengthStruct):
    # fileHandle should be opened binary append 'ab'
    packed1 = bytes(word1, 'ASCII')
    packed2 = bytes(word2, 'ASCII')
    packedAline = scoreStruct.pack(alineScore)
    packedCons = scoreStruct.pack(consScore)
    NEWLINE = b'\n'

    length = len(word1) + len(word2) + 11 # the 11 = 8+2+1 is for the two floats at the end, plus the length itself, plus the null byte
    packedLength = lengthStruct.pack(length)

    fileHandle.write(packedLength)
    fileHandle.write(packed1)
    fileHandle.write(b'\x00')
    fileHandle.write(packed2)
    fileHandle.write(packedAline)
    fileHandle.write(packedCons)


def writeFinalBytes(fileHandle, lengthStruct):
    ''' this function will write a packed short int with value 0, this signifies the end of the file '''
    packedLength = lengthStruct.pack(0)
    fileHandle.write(packedLength)


def writeToText(fileName, word1, word2, alineScore, consScore):
    with open(fileName, 'a') as file:
        file.write("\t".join((word1, word2, str(alineScore), str(consScore) + "\n")))


def readFromBinary(fileName):
    ''' each word pair is represented with two bytes indicating the length of the bytes for this word pair, the two words in ascii (separated with a null byte), and
    followed by 8 bytes for the two score float values 

    [length 2 bytes][word1 ASCII][NULL][word2 ASCII][alineScore][consScore]

    '''

    scoresDict = {} # this dict will map tuples of the words to a tuple containing each type of score
    # rather than creating two dicts and having to use memory for all the key tuples twice


    scoreStruct = Struct('f') # float format
    lengthStruct = Struct('H') # short int format

    with open(fileName, 'rb') as file:
        content = file.read()
        totalLength = len(content)
        startIndex = 0
        packedLength = content[startIndex:startIndex+2]
        length = lengthStruct.unpack(packedLength)[0]
        #sys.stderr.write("\n")
        while length != 0:

            nextIndex = startIndex + length # the index at this end of this word pair, i.e. where to find the next packedLength

            words = content[startIndex+2 : nextIndex-8] # the last eight bytes are for the 2 floats so grab everything before

            wordParts = words.split(b'\x00') # the words are split by a null char
            
            wordTuple = tuple(wordParts)

            alineScorePack = content[nextIndex-8:nextIndex-4]
            consScorePack  = content[nextIndex-4:nextIndex]
            alineScore = scoreStruct.unpack(alineScorePack)[0]
            consScore = scoreStruct.unpack(consScorePack)[0]

            scoresDict[wordTuple] = (alineScore, consScore)

            startIndex = nextIndex # move start index to the next word pair

            # look at the next chunk
            packedLength = content[nextIndex : nextIndex+2]
            length = lengthStruct.unpack(packedLength)[0]

        return scoresDict


'''
moved to alignmentFeatures.py Nov. 11

def lookUpWordPair(scoresDict, aline1, aline2):
    bytes1 = bytes(aline1, "ASCII")
    bytes2 = bytes(aline2, "ASCII")
    wordTuple1 = (bytes1, bytes2)
    wordTuple2 = (bytes2, bytes1) # can't be sure what order they are in (unless we look at accs? TODO?)

    #print("looking for {0} or {1}".format(wordTuple1, wordTuple2))
    if wordTuple1 in scoresDict:
        #print("found in alignment dict")
        score, normalizedAlignedConsonants = scoresDict[wordTuple1]
    elif wordTuple2 in scoresDict:
        #print("found in alignment dict")
        score, normalizedAlignedConsonants = scoresDict[wordTuple2]
    else:
        print("not found in alignment dict")
        print("aline 1 = {0}, aline2 = {1}".format(aline1, aline2))
        score, normalizedAlignedConsonants  = getAlignmentFeatures(aline1, aline2) # they not in the dict somehow; shouldnt happen


    return score, normalizedAlignedConsonants

'''

if __name__ == "__main__":

    # the two words (in ALINE representation) and their ALINE score from nusimil, and the normalized number of aligned consonants
    word1 = 'aheHw'
    word2 =  "ahiHha"
    alineScore = 0.396825891033
    consScore = 0.5345352522432

    bytesFileName = "exampleScores.bin"
    textFileName = "exampleScores.txt"

    scoreStruct = Struct('f') # float format
    lengthStruct = Struct('H')

    # open the file once as write to clear it
    with open(bytesFileName, 'w') as file:
        pass
    with open(textFileName, 'w') as file:
        pass

    with open(bytesFileName, 'ab') as file:
        for i in range(100):
            writeToBinary(file, word1, word2, alineScore, consScore, scoreStruct, lengthStruct)
            writeToText(textFileName, word1, word2, alineScore, consScore)
        writeFinalBytes(file, lengthStruct) # write the 0 bytes to indicate end of file

    scoresDict = readFromBinary(bytesFileName)
    print(scoresDict)


