
import re

class CogSetFileReader(object):

    def __init__(self, fileName):
        self.numToCognateSet = self.readFileIntoDict(fileName)


    def readFileIntoDict(self, fileName):
        ''' function to read a file and return a dictoinary with keys as cognate set numbers and values as list of words in set. '''

        result = {}

        with open(fileName) as file:
            textFile = file.read()
            cogSets = textFile.split("\n\n\n")
            while cogSets[-1] == "":
                cogSets.pop() # may be an empty cogset at the end of file


            numPattern = "^Set Number (\d+)"
            wordPattern = "^([A-Z]+)\t([^\t]+)\t([^\t]+)$" #the word and def are one or more non-tabs

            num1LanguageSets = 0
            num1WordSets = 0
                    
            for cogSet in cogSets:
                match = re.search(numPattern, cogSet)
                if match is None:
                    print(cogSet)
                    exit() # problem with file read in
                else:
                    cogNum = int(match.groups()[0])

                matchWords = re.findall(wordPattern, cogSet, re.MULTILINE)
                # matchWords is a list of tuples of (Acc, word, definition), e.g. [('F', 'wiːhkweːpičikani', 'bundle'), ('M', 'wiahkiːhpečekan', 'bundle')]

                if matchWords is None:
                    print(cogSet)
                    exit() # problem with file read in
                elif len(matchWords) < 2: # don't include sets with only one word (why is this even a cognate set?)
                    #print("match of length {1} with setNum = {0}".format(cogNum, len(matchWords)))
                    num1WordSets += 1
                    #result[cogNum] = matchWords # if want to add cognate sets of a single word
                    continue
                else:
                    accSet = set()
                    for matchTuple in matchWords:
                        accSet.add(matchTuple[0])

                    if len(accSet) == 1:
                        num1LanguageSets += 1
                    #print("cog num adding = {0}".format(cogNum))
                    result[cogNum] = matchWords
        #print("num 1 word sets = {0}".format(num1WordSets))
        return result


    def getNumToCognateSet(self):
        return self.numToCognateSet


    def __len__(self):
        return len(self.numToCognateSet)

    def at(self, cogNum):
        return self.numToCognateSet[cogNum]

    def __getitem__(self, cogNum):
        return self.numToCognateSet[cogNum]

    def __iter__(self):
        return iter(sorted(self.numToCognateSet))

    def __contains__(self, item):
        return item in self.numToCognateSet
