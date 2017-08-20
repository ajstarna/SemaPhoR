''' class used to read in Def Sets files like the outputs of  findIdenticalDefs.py '''



class DefSet(object):

    def __init__(self):
        self.defn = ""
        self.wordTupleList = []


    def setDefinition(self, defn):
        self.defn = defn

    def addWordTuple(self, wordTuple):
        self.wordTupleList.append(wordTuple)


    def __iter__(self):
        # this method lets us write 'for wordTuple in DefSet' instead of having to access DefSet.wordTupleList
        return iter(self.wordTupleList)


    def __len__(self):
        return len(self.wordTupleList)

    def __hash__(self):
        return hash(tuple(self.wordTupleList))

    def __getitem__(self, index):
        return self.wordTupleList[index]

    def __repr__(self):
        # the method which is called when printing
        result = self.defn + "\n"
        for wordTuple in self.wordTupleList:
            result += "\t".join(wordTuple) + "\n"
        return result.strip() # remove last newline from the end
        

class DefSetsReader(object):

    def __init__(self, defSetsFile=None):
        if defSetsFile is None:
            return
        self.readFile(defSetsFile)


    def readFile(self, defSetsFile):
        with open(defSetsFile) as file:
            text = file.read()
            rawDefSets = text.split("\n\n")
            rawDefSets.pop() # last is empty

        self.defSets = []
        self.numDict = {} # the num dict maps a set number to a def set
        setNum = 1
        for rawDefSet in rawDefSets:
            newDefSet = self.processDefSet(rawDefSet)
            self.defSets.append(newDefSet)
            self.numDict[setNum] = newDefSet
            setNum += 1


    def processDefSet(self, defSet):
        newDefSet = DefSet()
        lines = defSet.split("\n")
        defn = lines.pop(0) # first line is the shared definition
        newDefSet.setDefinition(defn)
        for line in lines:
            wordTuple = tuple(line.split("\t"))
            newDefSet.addWordTuple(wordTuple)
        return newDefSet


    def __iter__(self):
        return iter(self.defSets)

    def size(self):
        return len(self.defSets)

    def __len__(self):
        return len(self.defSets)

    def __getitem__(self, index):
        return self.defSets[index]
