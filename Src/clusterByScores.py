#!/usr/bin/env python3

''' 
this script will merge clusters together that have a total score 
'''

import re
import sys
from collections import defaultdict, OrderedDict
from DefSetsReader import DefSetsReader
from ClassifiedPairsReader import ClassifiedPairsReader

from LanguageDictParser import AlgonquianLanguageDictParser

from copy import deepcopy

class Cluster(object):
    def __init__(self, originalTupleList):
        self.wordTuplesList = originalTupleList
        self.avgSim = 0
        self.totalSim = 0
        self.numCompares = 0
        #self.clusterString = "-".join([str(orig) for orig in originalTupleList])
        self.additionOrder = [(deepcopy(originalTupleList), None)] # keep tracks of the order and avg score when adding a new word
        # starts as simply the original tuple with a score of None

    def merge(self, other, avg, total, numComps):
        # given another cluster, merge by combining the wordlists and updating similarity stats
        self.totalSim = self.totalSim + total
        self.numCompares = self.numCompares + numComps
        self.avgSim = self.totalSim / self.numCompares
        self.wordTuplesList.extend(other.wordTuplesList)
        self.additionOrder.append((other.additionOrder, avg))
                                  
    def __iter__(self):
        return iter(sorted(self.wordTuplesList))

    def __len__(self):
        return len(self.wordTuplesList)

    def __lt__(self, other):
        # so we can sort a list of clusters
        # if our avgSim is less than the other Cluster's avgSim then return True
        return self.avgSim < other.avgSim


class Clusterer(object):
    def __init__(self, classifiedPairsFile, clustersFile, mergeThreshold, progress, displayOrder, noSameLang):
        self.clustersFile = clustersFile
        self.mergeThreshold = mergeThreshold
        self.progress = progress
        self.displayOrder = displayOrder
        self.noSameLang = noSameLang

        sys.stderr.write("reading pairs...\n")
        t1 = time.clock()
        self.pairsReader = ClassifiedPairsReader(classifiedPairsFile, bothWays=False)
        t2 = time.clock()
        sys.stderr.write("time to read pairs was {0:.2f}m\n".format((t2-t1)/60.0))
        sys.stderr.write("Initializing clusters...\n")
        self.initializeClusters()
        t1 = time.clock()
        sys.stderr.write("Initializing score mapping...\n")
        self.initializeMappingToScores()
        t2 = time.clock()
        sys.stderr.write("took {0:.2f}m\n".format((t2-21)/60.0))
        sys.stderr.write("Initializing Similarities...\n")
        t1 = time.clock()
        self.initializeSimilarities()       
        t2 = time.clock()
        sys.stderr.write("took {0:.2f}m\n".format((t2-21)/60.0))



    def reportTimes(self):
        sys.stderr.write("Number of merges = {0}\n".format(self.count))
        sys.stderr.write("Time updating similarities = {0:.2f}m\n".format(self.similarityTime/60.0))
        sys.stderr.write("Time setting similarities = {0:.2f}m\n".format(self.settingTime/60.0))
        sys.stderr.write("Time recalculating max similarity = {0:.2f}m\n".format(self.maxSimTime/60.0))
        sys.stderr.write("Total lookup time = {0:.2f}m\n".format(self.totalLookupTime/60.0))
        sys.stderr.write("Total cluster time = {0:.2f}m\n".format(self.totalClusterTime/60.0))
            

    def initializeMappingToScores(self):
        self.mappingToScores = {} # defaultdict(None)
        for wordTuple in self.pairsReader:
            currentAcc = wordTuple[0]
            otherTuplesWithScores = self.pairsReader[wordTuple]
            for other in otherTuplesWithScores:
                otherTuple = other[:-1]
                otherAcc = otherTuple[0]
                if currentAcc == otherAcc:
                    if self.noSameLang:
                        # if don't want any pairs of words from the same language, then don't put them in the mapping
                        continue
                    else:
                        score = 0
                else:
                    score = float(other[-1])
                self.mappingToScores[(wordTuple,otherTuple)] = score


    def addSimilarityScore(self, avgSim, totalSim, numCompares, clustIDA, clustIDB):
        self.allSimsList.append(avgSim)
        self.simsToClusterIDs[avgSim].add((clustIDA,clustIDB))
        self.similarityDict[clustIDA][clustIDB] = (avgSim, totalSim, numCompares)


    def initializeSimilarities(self):
        ''' calculates the similarity between each pair of clusters and stores them in a dict of dicts. 
            Also initalizes the maxSim tuple '''

        self.similarityDict = defaultdict(dict) # a defualt dict (of a dict) will assume that an entry is an empty dict

        self.totalLookupTime = 0
        self.simsToClusterIDs = defaultdict(set) # this reverse mapping will map a simialrity score to a list of (clustID1, clustID2) tuples with that score
        self.allSimsList = [] # this will keep a sorted copy of the similarities so it is easy to get the next best one without having to sort the keys of simsToClusterIDs every time


        sys.stderr.write("\n")
        for clustIDA in self.clusterDict:
            sys.stderr.write("\033[F")
            sys.stderr.write("set {0} / {1}\n".format(clustIDA, len(self.clusterDict)))

            for clustIDB in self.clusterDict:
                if clustIDB <= clustIDA:
                    # we only want to look at clusters with a higher ID number
                    continue

                avgSimilarity, totalSimilarity, numCompares = self.calculateClusterSimilarity(clustIDA, clustIDB)
                if avgSimilarity is None:
                    # if avg Sim is None, this means that none of the words between this clusters have a comparison
                    # therefore we don't add anything to the similarity lists on dictionaries
                    continue

                self.addSimilarityScore(avgSimilarity, totalSimilarity, numCompares, clustIDA, clustIDB)

        sys.stderr.write("Total lookup time = {0:.2f}m\n".format(self.totalLookupTime/60.0))
        self.allSimsList.sort()

            
    def calculateClusterSimilarity(self, clustIDA, clustIDB):
        ''' given two cluster IDs (A < B) it calculates the average similarity between them '''
        clusterA = self.clusterDict[clustIDA]
        clusterB = self.clusterDict[clustIDB]

        totalSimilarity = 0
        numCompares = 0

        for wordTuple1 in clusterA:
            for wordTuple2 in clusterB:
                t1 = time.clock()
                similarity = self.lookupScoreBetweenTuples(wordTuple1, wordTuple2)
                t2 = time.clock()
                self.totalLookupTime += (t2 - t1)
                if similarity is None:
                    continue # don't count towards average: perhaps too lenient
                    #return (-1, -1, 0) # harsh: if any word pair not compared then punish the whole set: negative to whole setwise
                    #similarity = -1 # give negative to just the current element: a nice middle ground?

                totalSimilarity += similarity
                numCompares += 1

        if numCompares == 0:
            #sys.stderr.write("A similarity calculation with 0 comparrisons!\n")
            #print(clusterA)
            #print(clusterB)
            #return (float("-inf"), float("-inf"), 0)
            return None, None, 0

        avgSimilarity = float(totalSimilarity)/numCompares 

        return (avgSimilarity, totalSimilarity, numCompares)


    def lookupScoreBetweenTuples(self, wordTuple1, wordTuple2):
        # not sure which direction this tuple could be in the mapping, so check both
        if (wordTuple1, wordTuple2) in self.mappingToScores:
            return self.mappingToScores[(wordTuple1, wordTuple2)]
        if (wordTuple2 ,wordTuple1) in self.mappingToScores:
            return self.mappingToScores[(wordTuple2, wordTuple1)]
        # if not in the mapping period, then return None
        return None




    def cluster(self):
        ''' main method to call to cluster the already read-in sets '''

        self.similarityTime = 0
        self.maxSimTime = 0
        self.settingTime = 0
        self.totalClusterTime = 0

        self.count = 0
        while len(self.clusterDict) > 1:
            start = time.clock()
            maxSim = self.getMaxSimilarity() # the IDs of the two clusters with the current max similarity
            self.maxSimTime += time.clock()-start


            if maxSim is None or  maxSim <= self.mergeThreshold:
                break

            clustIDA, clustIDB = sorted(self.simsToClusterIDs[maxSim], reverse=True)[0] # could be more than one cluster pair with the max current score
            if self.progress:
                sys.stderr.write("{0} Clusters, MaxSim: {1} between {2} and {3}!\n".format(len(self.clusterDict), maxSim, clustIDA, clustIDB))
            self.merge(clustIDA, clustIDB) # merge these two clusters

            self.removeSimilarityScore(maxSim, clustIDA, clustIDB)

            start2 = time.clock()
            self.updateSimilarities(clustIDA, clustIDB) # update the similarity for those pairs involving these two clusters
            self.similarityTime += time.clock()-start2

            del self.clusterDict[clustIDB] # get rid of clustIDB in the clustDict

            self.count += 1
            self.totalClusterTime += time.clock() - start
            if self.progress and self.count % 100 == 0:
                self.reportTimes()

        self.writeClusters()
        self.reportTimes()


    def merge(self, clustIDA, clustIDB):
        ''' given two cluster IDs, merges B into A.
            Note that B is still referenced in the cluster list and similarity dict. This gets removed later on'''

        avg, total, numComps = self.similarityDict[clustIDA][clustIDB]
        self.clusterDict[clustIDA].merge(self.clusterDict[clustIDB], avg, total, numComps)


    def getMaxSimilarity(self):
        while True:
            try:
                maxSimilarity = self.allSimsList.pop()
            except IndexError:
                return None
            if maxSimilarity in self.simsToClusterIDs:
                # it is possible that this score doesn't actually exist anymore
                # when we update the scores we only update simsToClusterIDs since it is a dictionary and way faster
                # the allSimsList still contains all old similarities and are only seen now when we pop
                # if the score does exist, then we break the loop
                break
        return maxSimilarity


    def updateSimilarities(self, clustIDKept, clustIDGone):
        ''' given the ID of two clusters that have now been merged into clustKept, update the similarities dictionary for any pair
            involving either of the clusters. Any similarity to cluster Gone needs to be removed  and similarities to cluster
            Kept need to be recalculated. '''
        # all IDs before Kept in the cluster list need to update their similarity dictionary

        for clustIDCurrent in self.clusterDict:
            if clustIDCurrent == clustIDKept or clustIDCurrent == clustIDGone:
                continue

            newAvgSim, newTotalSim, newNumComp = self.getNewSimilaritiesAndRemoveOldInDicts(clustIDCurrent, clustIDKept, clustIDGone)
            if newAvgSim is not None:
                if clustIDCurrent < clustIDKept:
                    self.addSimilarityScore(newAvgSim, newTotalSim, newNumComp, clustIDCurrent, clustIDKept)
                else:
                    self.addSimilarityScore(newAvgSim, newTotalSim, newNumComp, clustIDKept, clustIDCurrent)
        self.allSimsList.sort() # now we sort the all sims list so that when we want to find the max next time we simply need to pop


    def removeSimilarityScore(self, sim, clustIDA, clustIDB):
        self.simsToClusterIDs[sim].remove((clustIDA, clustIDB))
        if self.simsToClusterIDs[sim] == set():
            del self.simsToClusterIDs[sim]
        del self.similarityDict[clustIDA][clustIDB]
        # note: theoretically you could remove the sim from self.allSimsList here as well;
        # however this would be order(n) time for every removal
        # instead, leave the sim in the list and be "lazy" about deletion.
        # when we check a new max simlarity we will just need to check if that similarity is 
        # still in the simsToClusterIDs dictionary which holds the "true" similarities between clusters.


    def getNewSimilaritiesAndRemoveOldInDicts(self, clustIDCurrent, clustIDKept, clustIDGone):
        ''' given the id of the current cluster (which we are going to update) and the IDs of the two clusters which were merged (into the Kept one)
            we set the new similarity of Current and Kept by using the already calculated similarities between current and Kept and current and Gone. 
            Rather than recalculate using the pairwise scores. '''

        # need to remove these scores from the similarityToClusterIDs dictionary
        # since the score
        if clustIDCurrent < clustIDKept:
            # current is below kept so the similarity is stored in current's dict
            if clustIDKept in self.similarityDict[clustIDCurrent]:
                avgSimKept, totalSimKept, numCompKept = self.similarityDict[clustIDCurrent][clustIDKept]
                self.removeSimilarityScore(avgSimKept, clustIDCurrent, clustIDKept)
            else:
                avgSimKept, totalSimKept, numCompKept = None, None, 0
        else:
            # else similarity is stored in Kept's dictionary
            if clustIDCurrent in self.similarityDict[clustIDKept]:
                avgSimKept, totalSimKept, numCompKept = self.similarityDict[clustIDKept][clustIDCurrent]
                self.removeSimilarityScore(avgSimKept, clustIDKept, clustIDCurrent)
            else:
                avgSimKept, totalSimKept, numCompKept = None, None, 0

        if clustIDCurrent < clustIDGone:
            # current is below Gone so the similarity is stored in current's dict
            if clustIDGone in self.similarityDict[clustIDCurrent]:
                avgSimGone, totalSimGone, numCompGone = self.similarityDict[clustIDCurrent][clustIDGone]
                self.removeSimilarityScore(avgSimGone, clustIDCurrent, clustIDGone)
            else:
                avgSimGone, totalSimGone, numCompGone = None, None, 0
        else:
            # else similarity is stored in Gone's dictionary
            if clustIDCurrent in self.similarityDict[clustIDGone]:
                avgSimGone, totalSimGone, numCompGone = self.similarityDict[clustIDGone][clustIDCurrent]
                self.removeSimilarityScore(avgSimGone, clustIDGone, clustIDCurrent)
            else:
                avgSimGone, totalSimGone, numCompGone = None, None, 0

        if avgSimKept is None or avgSimGone is None:
            return (None, None, 0)

        elif avgSimKept is None:
            newNumComp =  numCompGone
            newTotalSim = totalSimGone
            newAvgSim = avgSimGone

        elif avgSimGone is None:
            newNumComp =  numCompKept
            newTotalSim = totalSimKept
            newAvgSim = avgSimKept

        else:
            newNumComp = numCompKept + numCompGone
            newTotalSim = totalSimKept + totalSimGone
            newAvgSim = float(newTotalSim) / newNumComp

        return (newAvgSim, newTotalSim, newNumComp)
        

    def writeClusters(self):
        ''' once the clustering is done, we can print them out '''
        with open(self.clustersFile, 'w') as file:
            for i, cluster in enumerate(sorted(self.clusterDict.values(), reverse=True)): # sort by avergae similarity of clusters
                if len(cluster) == 1:
                    continue
                file.write("Cluster {0}: Average Similarity = {1:.3f}\n".format(i, cluster.avgSim))
                for wordTuple in cluster:
                    file.write("\t".join(wordTuple) + "\n")
        
                if self.displayOrder:
                    file.write("Order of Additions:\n")
                    for additionScore in cluster.additionOrder:
                        file.write(str(additionScore) + "\n")
                file.write("\n")


    def writeGraphFile(self, outputGraphFile):
        with open(outputGraphFile, 'w') as file:
            # start with the vertices section
            numVertices = len(self.clusterDict)
            file.write("*Vertices {0}\n".format(numVertices)) # each word is in a cluster and hence its own vertex to start
            for clusterNum in self.clusterDict:
                wordTuple = self.clusterDict[clusterNum].wordTuplesList[0] # should only have one wordTuple in it
                tupleAsString = "\t".join(wordTuple)
                #file.write(str(clusterNum))
                #file.write(tupleAsString)
                file.write(' {0} "{1}"\n'.format(clusterNum, tupleAsString))
            
            # then do the edges section
            numEdges = 0
            for clusterNum in self.similarityDict:
                mappingToOthers = self.similarityDict[clusterNum]
                numEdges += len(mappingToOthers)
            file.write("*Edges {0}\n".format(numEdges))
            for clusterNum in sorted(self.similarityDict.keys()):
                mappingToOthers = self.similarityDict[clusterNum]
                for otherNum in sorted(mappingToOthers.keys()):
                    avg, total, numComps = mappingToOthers[otherNum]
                    file.write("{0} {1} {2}\n".format(clusterNum, otherNum, avg)) # edge is the two node nums followed by the weight
            




class FromSetsClusterer(Clusterer):

    def __init__(self, setsFile, classifiedPairsFile, clustersFile, mergeThreshold, progress, displayOrder, noSameLang):
        # takes the file of sets already created by stage 1 or 1B etc.
        sys.stderr.write("reading sets...\n")
        self.setsReader = DefSetsReader(setsFile)
        super().__init__(classifiedPairsFile, clustersFile, mergeThreshold, progress, displayOrder, noSameLang)


    def initializeClusters(self):
        ''' method to set up the cluster dictionary and cluster list'''

        self.clusterDict = OrderedDict() # the cluster dict maps from an ID to a list of wordTuples

        # the cluster IDs start as the index of the def set in the file
        for i, defSet in enumerate(self.setsReader):
            self.clusterDict[i] = Cluster(defSet.wordTupleList) # each cluster starts out as the list of cluster in that defSet
            #print("cluster dict [{0}] = {1}".format(i, defSet.wordTupleList))



class FromLangDictsClusterer(Clusterer):
    def __init__(self, classifiedPairsFile, clustersFile, mergeThreshold, progress, displayOrder, noSameLang):
        sys.stderr.write("reading lang dicts...\n")
        #if options.small:
        #    self.langReader = AlgonquianLanguageDictParserSmall()
        #else:
        self.langReader = AlgonquianLanguageDictParser()

        super().__init__(classifiedPairsFile, clustersFile, mergeThreshold, progress, displayOrder, noSameLang)


    def initializeClusters(self):
        ''' method to set up the cluster dictionary and cluster list'''

        self.clusterDict = OrderedDict() # the cluster dict maps from an ID to a list of cluster
        self.langDicts = self.langReader.parseAllFiles()

        clustID = 0
        for langAcc in sorted(self.langReader.langs):
            langDict = self.langDicts[langAcc]
            #count = 0
            for word in sorted(langDict):
                #count += 1
                #if count > 2000:
                #    break
                definitions = langDict[word]
                for defn in definitions:
                    wordTuple = (langAcc, word, defn)
                    self.clusterDict[clustID] = Cluster([wordTuple]) # each cluster starts out as one word by itself.
                    clustID += 1


class WithSubstringClusterer(FromLangDictsClusterer):
    # this class uses classified pairs from the general SVM (like the super class), but also takes in those same pairs
    # classified by the substring SVM
    def __init__(self, generalClassifiedPairsFile, clustersFile, substringClassifiedPairsFile, substringWeight, mergeThreshold, progress, displayOrder, noSameLang):
        sys.stderr.write("reading substring pairs...\n")
        t1 = time.clock()
        self.substringPairsReader = ClassifiedPairsReader(substringClassifiedPairsFile, bothWays=True)
        t2 = time.clock()
        sys.stderr.write("time to read substring pairs was {0:.2f}m\n".format((t2-t1)/60.0))
        self.substringWeight = substringWeight

        super().__init__(generalClassifiedPairsFile, clustersFile, mergeThreshold, progress, displayOrder, noSameLang)


    def initializeMappingToScoresFromSubstringPairs(self):
        self.mappingToScores = {} 

        for wordTuple in self.substringPairsReader:
            currentAcc = wordTuple[0]
            otherTuplesWithScores = self.pairsReader[wordTuple]
            for other in otherTuplesWithScores:
                otherTuple = other[:-1]
                otherAcc = otherTuple[0]
                if currentAcc == otherAcc:
                    if self.noSameLang:
                        # if don't want any pairs of words from the same language, then don't put them in the mapping
                        continue
                    else:
                        score = 0
                else:
                    score = float(other[-1])

                ''' Since we just give a score of 0 anyways to these, doesn't really matter...?
                if (wordTuple,otherTuple) in self.mappingToScores:
                    # when reading in pairs from the same language, they will have two entrees in the substring classified
                    # pairs file (since it is not symmetric.
                    # therefore, we look for them to appear twice and simply average the score between both times occuring
                    # note: (is it possible that in one direction we have a positive score and one direction a negative score?
                    # -then will only appear once in the positive classified pairs, guess thats ok just take that one score)
                    previousScore = self.mappingToScores[(wordTuple,otherTuple)]
                    self.mappingToScores[(wordTuple,otherTuple)] = (prevousScore + score)/2
                else:
                '''
                self.mappingToScores[(wordTuple,otherTuple)] = score


    def initializeMappingToScores(self):
        self.initializeMappingToScoresFromSubstringPairs() # first fill it with the substring scores

        for wordTuple in self.pairsReader:
            currentAcc = wordTuple[0]
            otherTuplesWithScores = self.pairsReader[wordTuple]
            for other in otherTuplesWithScores:
                otherTuple = other[:-1]
                otherAcc = otherTuple[0]
                if currentAcc == otherAcc:
                    if self.noSameLang:
                        # if don't want any pairs of words from the same language, then don't put them in the mapping
                        continue
                    score = 0
                else:
                    score = float(other[-1])

                if (wordTuple,otherTuple) in self.mappingToScores:
                    substringScore = self.mappingToScores[(wordTuple,otherTuple)]
                    self.mappingToScores[(wordTuple,otherTuple)] = (substringScore * self.substringWeight) + (score * (1 - self.substringWeight))
                else:
                    # if it wasnt already in mappingToScores from the substring pairs, then that means
                    # it didn't get a positive score from that model, so we don't add it here.
                    continue



if __name__ == "__main__":

    import optparse
    import time

    parser = optparse.OptionParser()
    parser.add_option('-s', action='store', dest='setsFile', help="Name of def sets file. Only required if clustering starting from some already existing clusters.")
    parser.add_option('-l', action='store_true', dest='langDicts', help="Use if want to start clustering from scratch, i.e. the language dicts.", default=False)

    parser.add_option('-p', action='store', dest='classifiedPairsFile', help="Required: name of classified pairs from the general SVM.")
    parser.add_option('--sp', action='store', dest='substringClassifiedPairsFile', help="name of classified pairs for the substring SVM.", default=None)
    parser.add_option('--sw', action='store', dest='substringWeight', help="weight of the substring score versus the general score.", default=0.5)

    parser.add_option('--noSameLang', action='store_true', dest='noSameLang', help="flag if want to NOT allow pairs of same languages at all when clustering.", default=False)

    parser.add_option('--graph', action='store', dest='outputGraphFile', help="name of output graph file ex: 'similarityGraph.net' which can be fed to the infomap code", default=None)
    parser.add_option('--cluster', '-c', action='store', dest='clustersFile', help="name of output cluster file", default=None)

    parser.add_option('-t', action='store', dest='mergeThreshold', help="the threshold for merging. default = 0", default=0)
    parser.add_option('--progress', action='store_true', dest='progress', help="Use if want to print to stderr the progress.", default=False)
    parser.add_option('--order', action='store_true', dest='displayOrder', help="Use if want to print the order with avg scores of when clusterd were merged.", default=False)



    options, args = parser.parse_args()

    if  options.classifiedPairsFile is None or options.clustersFile is None:
        parser.print_help()
        exit()


    if options.langDicts == False and options.setsFile is None:
        parser.print_help()
        exit()


    mergeThreshold = float(options.mergeThreshold)

    start = time.clock()
    if options.langDicts:
        if options.substringClassifiedPairsFile is not None:
            weight = float(options.substringWeight)
            clust = WithSubstringClusterer(options.classifiedPairsFile, options.clustersFile, options.substringClassifiedPairsFile, weight, 
                                           mergeThreshold, options.progress, options.displayOrder, options.noSameLang)
        else:
            clust = FromLangDictsClusterer(options.classifiedPairsFile, options.clustersFile, mergeThreshold, options.progress, options.displayOrder, options.noSameLang)
    else:
        clust = FromSetsClusterer(options.setsFile, options.classifiedPairsFile, options.clustersFile, mergeThreshold, options.progress, options.displayOrder, options.noSameLang)


    if options.outputGraphFile is not None:
        clust.writeGraphFile(options.outputGraphFile)
    clust.cluster()

    end = time.clock()
    sys.stderr.write("Total time of execution = {0:.2f}m\n".format((end-start)/60.0))


