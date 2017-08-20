#!/usr/bin/env python3


import re
from collections import defaultdict
import sys

class ClassifiedPairsReader(object):
    ''' class to read in the classified  pair file (with the pairs and score and features) and populate a pairDict'''
    def __init__(self, pairFileName, bothWays=True):
        self.bothWays = bothWays # bothWays==True makes the second word of each compared pair have an entry in the dict as well
        # for grouping into protoSets, want bothWays=False since only want to group the words INTO protosets, not the words already in them
        self.pairSets = self.readFileIntoPairSets(pairFileName)
        self.pairDict = self.createPairDict()


    def readFileIntoPairSets(self, fileName):
        with open(fileName) as file:
            textFile = file.read()
            pairSets = textFile.split("\n\n")
            while pairSets[-1] == "":
                pairSets.pop() # if end set is empty
        return pairSets
    

    def getWordPattern(self):
        wordPattern = "^([A-Z])\t([^\t]+)\t([^\t]+)$"
        return wordPattern

    def createPairDict(self):
        ''' given the pair sets, this creates a dict self.pairDict where key is the compare word tuple (acc, word, defn) and 
        value is a list of tuples (acc, word, defn, SVMValue) '''

        pairDict = defaultdict(list)
        SVMPattern = "Value: ([^\n]+)"
        wordPattern = self.getWordPattern()
        for pairSet in self.pairSets:
            SVMmatch = re.search(SVMPattern, pairSet) # use regex to find the svm value
            wordmatch = re.findall(wordPattern, pairSet, re.MULTILINE) # use regex to find the two words in this set
            if SVMmatch is None:
                continue # something is weird with this set so move on

            SVMvalue = SVMmatch.groups(0)#[0] # a tuple with just the SVMvalue

            try:
                compareTuple = wordmatch[0]
            except:
                sys.stderr.write("problem with \n{0}\n".format(pairSet))
                exit(-1)

            otherWordTuple = wordmatch[1] # the other word acc,word,defn tuple
            try:
                value = otherWordTuple + SVMvalue # the value is the (acc, word, defn, svmScore) of the other word
            except:
                print("Problem with otherTuple = {0} and SVMvalue = {1}".format(otherWordTuple, SVMvalue))
                print("SVMmatch.groups(0) = {0}".format(SVMmatch.groups(0)))
                exit()


            pairDict[compareTuple].append(otherWordTuple + SVMvalue) # add it to the list of other values for this compar word
            # this is why we use a defaultdict(list), since assumes there is an empty list at this key when not used yet

            if self.bothWays:
                pairDict[otherWordTuple].append(compareTuple + SVMvalue) # add the other direction, 

        return pairDict

    def __getitem__(self, item):
        return self.pairDict[item]

    def getPairDict(self):
        return self.pairDict

    def __iter__(self):
        return iter(self.pairDict)

    def __len__(self):
        return len(self.pairDict)



class ClassifiedPairsReaderWithHopelessPairs(ClassifiedPairsReader):
    # this reads in the pairs an can analyze the features to find "hopeless" pairs, i.e. 
    # pairs that don't fire any definition features

    def createPairDict(self):
        ''' given the pair sets, this creates a dict self.pairDict where key is the compare word tuple (acc, word, defn) and 
        value is a list of tuples (acc, word, defn, SVMValue) '''

        pairDict = defaultdict(list)
        self.hopelessPairs = set()

        SVMPattern = "Value: ([^\n]+)"
        wordPattern = self.getWordPattern()
        featurePattern = "[0-9]+:[0-9]+"

        for pairSet in self.pairSets:
            SVMmatch = re.search(SVMPattern, pairSet) # use regex to find the svm value
            wordmatch = re.findall(wordPattern, pairSet, re.MULTILINE) # use regex to find the two words in this set

            if SVMmatch is None:
                continue # something is weird with this set so move on

            SVMvalue = SVMmatch.groups(0)#[0] # a tuple with just the SVMvalue

            compareTuple = wordmatch[0]
            otherWordTuple = wordmatch[1] # the other word acc,word,defn tuple
            try:
                value = otherWordTuple + SVMvalue # the value is the (acc, word, defn, svmScore) of the other word
            except:
                print("Problem with otherTuple = {0} and SVMvalue = {1}".format(otherWordTuple, SVMvalue))
                print("SVMmatch.groups(0) = {0}".format(SVMmatch.groups(0)))
                exit()


            pairDict[compareTuple].append(otherWordTuple + SVMvalue) # add it to the list of other values for this compar word
            # this is why we use a defaultdict(list), since assumes there is an empty list at this key when not used yet

            if self.bothWays:
                pairDict[otherWordTuple].append(compareTuple + SVMvalue) # add the other direction, 


            featurematch = re.findall(featurePattern, pairSet)
            if self.isHopeless(featurematch):
                self.hopelessPairs.add((compareTuple, otherWordTuple))

        return pairDict


    def isHopeless(self, featurematch):
        # given a list of feature matches (eg: "2:0") this checks if any of the first 12 features are 1, in which case return False since not hopeless
        for feature in featurematch:
            featureNum, featureValue = feature.split(":")
            number = int(featureNum)
            value = int(featureValue)
            if number < 10 and value > 0:
                # if any of the first 9 features are 1 (the feature fired) then it is not hopeless
                #print("not hopeless: feature {0} has value {1}".format(number, value))
                return False
        return True


    def getHopelessPairs(self):
        return self.hopelessPairs




class ClassifiedPairsReaderCountWordNetFeatures(ClassifiedPairsReader):
    # this reads in the pairs an can analyze the features to find ones with several WordNet Features turned on
    # useful to find a good example for the paper

    wordNetCount = 1

    def createPairDict(self):
        ''' given the pair sets, this creates a dict self.pairDict where key is the compare word tuple (acc, word, defn) and 
        value is a list of tuples (acc, word, defn, SVMValue) '''

        pairDict = defaultdict(list)
        self.wordNetPairs = set() # this are pairs with 

        SVMPattern = "Value: ([^\n]+)"
        wordPattern = self.getWordPattern()
        featurePattern = "[0-9]+:[0-9]+"

        for pairSet in self.pairSets:
            SVMmatch = re.search(SVMPattern, pairSet) # use regex to find the svm value
            wordmatch = re.findall(wordPattern, pairSet, re.MULTILINE) # use regex to find the two words in this set

            if SVMmatch is None:
                continue # something is weird with this set so move on

            SVMvalue = SVMmatch.groups(0)#[0] # a tuple with just the SVMvalue

            compareTuple = wordmatch[0]
            otherWordTuple = wordmatch[1] # the other word acc,word,defn tuple
            try:
                value = otherWordTuple + SVMvalue # the value is the (acc, word, defn, svmScore) of the other word
            except:
                print("Problem with otherTuple = {0} and SVMvalue = {1}".format(otherWordTuple, SVMvalue))
                print("SVMmatch.groups(0) = {0}".format(SVMmatch.groups(0)))
                exit()


            pairDict[compareTuple].append(otherWordTuple + SVMvalue) # add it to the list of other values for this compar word
            # this is why we use a defaultdict(list), since assumes there is an empty list at this key when not used yet

            if self.bothWays:
                pairDict[otherWordTuple].append(compareTuple + SVMvalue) # add the other direction, 


            featurematch = re.findall(featurePattern, pairSet)
            numWordNet = self.enoughWordNet(featurematch)
            if numWordNet >= self.wordNetCount:
                #print(featurematch)
                self.wordNetPairs.add((compareTuple, otherWordTuple, numWordNet))

        return pairDict


    def enoughWordNet(self, featurematch):
        # given a list of feature matches (eg: "2:0") this checks enough of the word net features (4-9) are turned on
        total = 0
        for feature in featurematch:
            featureNum, featureValue = feature.split(":")
            number = int(featureNum)
            value = int(featureValue)
            if number > 8 and number < 10:
                total += value
        return total
        #if total >= self.wordNetCount:
        #    return True, total
        #else:
        #    return False, total


    def getWordNetPairs(self):
        return self.wordNetPairs
