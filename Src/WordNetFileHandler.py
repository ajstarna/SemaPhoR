''' this script is used to read in the lang_forms.txt, lang_synonyms.txt, etc files and populate a dict.
each line looks something like:
jump jumps jumped jumping
or
ambition  ambitiousness  aspiration  dream
or 
he takes a new stand    stand takes new
the keys are the first words(or defs) in each line and the values are a set of the following words in that line.

'''

from collections import defaultdict 
import sys

class WordNetFileHandler(object):
    def __init__(self, fileName):
        self.mappingDict = self.createMappingDict(fileName)


    def createMappingDict(self, fileName):
        mappingDict = defaultdict(set)
        with open(fileName) as file:
            for line in file:
                line = line.strip() # remove trailing newline
                if line == "":
                    continue # last line may be empty
                words = line.split() 
                try:
                    key = words.pop(0) # the first word is the key
                except:
                    print("error popping line = {0}".format(line))
                    exit(-1)
                #mappingDict[key] = set(words) # map the key to the remaining words from the line (as a set)
                mappingDict[key].update(set(words)) # Oct 12, in case the same key appears again on another line (hypernoyms only?)
        return mappingDict


    def at(self, lookup):
        ''' given a word (or a set), returns the set of coresponding mapping. May be empty.
        if the lookup is a set, then looks up each element in the set and unions them together to form the result'''
        if isinstance(lookup, str):
            return self.mappingDict[lookup]
        elif isinstance(lookup, set):
            result = set()
            for word in lookup:
                currentSet = self.mappingDict[word]
                result.update(currentSet)
            return result
        else:
            print("incorrect type given to lookup!")
            print(type(lookup))
            exit(-1)

    def belongsToSet(self, key, checkWord):
        ''' given a key and a checkWord, checks if the checkWord is in the mapping Set of the key and returns True or False. '''
        return checkWord in self.at(key)


