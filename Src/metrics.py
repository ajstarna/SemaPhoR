#!/usr/bin/env python3

''' this module contains the function for caluclating b-cubed value of a clustering along with other metrics, like C '''

from GoldEvaluator import GoldEvaluator

from collections import defaultdict




def bCubed(clustering, goldEvaluator, zeroWeightSingletons):

    # working B3

    ''' The clustering input is a dictionary from a cluster label to a list of (acc, word, defn) tuples within that cluster.
    The goldEvaluator is an object of type GoldEvaluator. Used to see if two words are cognate to eachother '''
    allRecalls = [] # keep track of the recall of each individual wordTuple
    allPrecisions = [] # keep track of the precision of each individual wordTuple
    recallWeights = []
    precisionWeights = []
    numNonZeros = 0
    numZeros = 0
    numWordsInClusters = 0
    numOfCognatesInASingleton = 0


    for clusterLabel in sorted(clustering):
        cluster = clustering[clusterLabel]
        clusterAsSet = set(cluster)
        numWordsInClusters += len(cluster)


        for wordTuple1 in cluster:
            # each wordTuple1 gets its own precision and (possibly) recall
            cogSet = goldEvaluator.getCogSetFromTuple(wordTuple1)
            if cogSet is None:
                numCogs = 1
                cognateMatches = 1

            else:
                numCogs = len(cogSet)
                cognateMatches = len(set(cogSet) & clusterAsSet)
               
            precision = float(cognateMatches) / len(cluster)
            allPrecisions.append(precision)

            recall = cognateMatches / float(numCogs)
            allRecalls.append(recall)

            if numCogs > 1 and len(cluster) == 1:
                numOfCognatesInASingleton += 1

            if zeroWeightSingletons:
                if numCogs > 1:
                    recallWeights.append(1.0)
                    precisionWeights.append(1.0)
                    numNonZeros += 1
                else:
                    recallWeights.append(0.0)
                    precisionWeights.append(0.0)
                    numZeros += 1
            else:
                recallWeights.append(1.0)
                precisionWeights.append(1.0)
                numNonZeros += 1
            #break
        #break
    '''
    print("Number of non zero-weighted = {0}".format(numNonZeros))
    print("Number of zero-weighted = {0}".format(numZeros))
    print("Number of words in clusters total = {0}".format(numWordsInClusters))
    print("Number of cognate words in singleton clusters = {0}".format(numOfCognatesInASingleton))
    '''
    recallDotProduct = sum( [allRecalls[i] * recallWeights[i] for i in range(len(allRecalls))] )
    #print("recall dot product = {0}".format(recallDotProduct))
    bcubedRecall = recallDotProduct / numNonZeros

    precisionDotProduct = sum( [allPrecisions[i] * precisionWeights[i] for i in range(len(allPrecisions))] )
    #print("precision dot product = {0}".format(precisionDotProduct))
    bcubedPrecision = precisionDotProduct / numNonZeros
    #print("precision = {0}".format(bcubedPrecision))

    bcubedFScore = 2 * bcubedRecall * bcubedPrecision / (bcubedRecall + bcubedPrecision)
    #print(allRecalls)
    #print(allPrecisions)
    return bcubedRecall, bcubedPrecision, bcubedFScore




def bCubed_0R(clustering, goldEvaluator, zeroWeightSingletons):
    ''' The clustering input is a dictionary from a cluster label to a list of (acc, word, defn) tuples within that cluster.
    The goldEvaluator is an object of type GoldEvaluator. Used to see if two words are cognate to eachother '''
    allRecalls = [] # keep track of the recall of each individual wordTuple
    allPrecisions = [] # keep track of the precision of each individual wordTuple
    recallWeights = []
    precisionWeights = []
    numNonZeros = 0
    numZeros = 0
    numWordsInClusters = 0
    numOfCognatesInASingleton = 0


    for clusterLabel in sorted(clustering):
        cluster = clustering[clusterLabel]
        clusterAsSet = set(cluster)
        numWordsInClusters += len(cluster)


        for wordTuple1 in cluster:
            # each wordTuple1 gets its own precision and (possibly) recall
            cogSet = goldEvaluator.getCogSetFromTuple(wordTuple1)
            if cogSet is None:
                numCogs = 1
                cognateMatches = 1
            else:
                numCogs = len(cogSet)
                cognateMatches = len(set(cogSet) & clusterAsSet)
               
            precision = float(cognateMatches) / len(cluster)
            allPrecisions.append(precision)

            recall = cognateMatches / float(numCogs)
            allRecalls.append(recall)

            if numCogs > 1 and len(cluster) == 1:
                numOfCognatesInASingleton += 1

            if zeroWeightSingletons:
                precisionWeights.append(1.0)

                if numCogs > 1:
                    recallWeights.append(1.0)
                    #precisionWeights.append(1.0)
                    #numNonZeros += 1
                else:
                    recallWeights.append(0.0)
                    #precisionWeights.append(0.0)
                    #numZeros += 1
            else:
                recallWeights.append(1.0)
                precisionWeights.append(1.0)
                #numNonZeros += 1
            #break
        #break
    '''
    print("Number of non zero-weighted = {0}".format(numNonZeros))
    print("Number of zero-weighted = {0}".format(numZeros))
    print("Number of words in clusters total = {0}".format(numWordsInClusters))
    print("Number of cognate words in singleton clusters = {0}".format(numOfCognatesInASingleton))
    '''
    recallDotProduct = sum( [allRecalls[i] * recallWeights[i] for i in range(len(allRecalls))] )
    #print("recall dot product = {0}".format(recallDotProduct))
    bcubedRecall = recallDotProduct / sum(recallWeights)#numNonZeros

    precisionDotProduct = sum( [allPrecisions[i] * precisionWeights[i] for i in range(len(allPrecisions))] )
    #print("precision dot product = {0}".format(precisionDotProduct))
    bcubedPrecision = precisionDotProduct / sum(precisionWeights)#numNonZeros
    #print("precision = {0}".format(bcubedPrecision))

    bcubedFScore = 2 * bcubedRecall * bcubedPrecision / (bcubedRecall + bcubedPrecision)
    #print(allRecalls)
    #print(allPrecisions)
    return bcubedRecall, bcubedPrecision, bcubedFScore




def bCubedMini(clustering, truth, mapping, zeroWeightSingletons):
    ''' The clustering input is a dictionary from a cluster label to a list of elements in that cluster.
    The truth is the true clustering
    The mapping, maps an element to its cluster label in the truth, i.e. inverse of the truth'''
    allRecalls = [] # keep track of the recall of each individual wordTuple
    allPrecisions = [] # keep track of the precision of each individual wordTuple
    allWeights = []
    numNonZeros = 0
    for clusterLabel in sorted(clustering):
        cluster = clustering[clusterLabel]
        for element1 in cluster:
            # each element1 gets its own precision and recall
            truthMatches = 0
            trueClusterLabel = mapping[element1]
            for element2 in cluster:
                if trueClusterLabel == mapping[element2]:
                    # for every other element in the cluster (including itself), see if cognate (will be at least once true)
                    truthMatches += 1
            precision = float(truthMatches) / len(cluster)
            allPrecisions.append(precision)
            
            trueCluster = truth[trueClusterLabel]
            sizeTruth = len(trueCluster)
            recall = truthMatches / float(sizeTruth)
            allRecalls.append(recall)
            

            if zeroWeightSingletons:
                if sizeTruth > 1:
                    allWeights.append(1.0)
                    numNonZeros += 1
                else:
                    allWeights.append(0.0)
            else:
                allWeights.append(1.0)
                numNonZeros += 1


    recallDotProduct = sum( [allRecalls[i] * allWeights[i] for i in range(len(allRecalls))] )
    bcubedRecall = recallDotProduct / numNonZeros

    precisionDotProduct = sum( [allPrecisions[i] * allWeights[i] for i in range(len(allPrecisions))] )
    bcubedPrecision = precisionDotProduct / numNonZeros

    bcubedFScore = 2 * bcubedRecall * bcubedPrecision / (bcubedRecall + bcubedPrecision)
    #print(allRecalls)
    #print(allPrecisions)
    return bcubedRecall, bcubedPrecision, bcubedFScore



def BUD(clustering, goldEvaluator):
    ''' The clustering input is a dictionary from a cluster label to a list of (acc, word, defn) tuples within that cluster.
    The goldEvaluator is an object of type GoldEvaluator. Used to see if two words are cognate to eachother 
    this method does our modified bCubed, aka BUD for buddies  where elements do not get points for matching with themselves.'''
    allRecalls = [] # keep track of the recall of each individual wordTuple
    allPrecisions = [] # keep track of the precision of each individual wordTuple
    numWordsInClusters = 0
    numOfCognatesNonPlaced = 0
    nonPlaced = set()

    #print("Number of clusters = {0}".format(len(clustering)))
    for clusterLabel in sorted(clustering):
        cluster = clustering[clusterLabel]
        numWordsInClusters += len(cluster)


        if len(cluster) == 1:
            wordTuple1 = cluster[0]
            cogSet1 = goldEvaluator.getCogSetFromTuple(wordTuple1)
            if not cogSet1 is None:
                # if the word in this cluster is from a cog set in the gold, then recall is zero since not placed in a set
                recall = 0
                allRecalls.append(recall)
                numOfCognatesNonPlaced += 1 # this was a word from a cog set but in its own cluster, i.e non-placed
                nonPlaced.add(wordTuple1 + (goldEvaluator.getCogNumFromTuple(wordTuple1),))
            # precision is undefined for these "non-placed" words in their own cluster
            continue


        for wordTuple1 in cluster:
            # each wordTuple1 gets its own precision and (possibly) recall
            cognateMatches = 0
            for wordTuple2 in cluster:
                if wordTuple1 == wordTuple2:
                    continue # don't compare with itself

                if goldEvaluator.areCognates(wordTuple1, wordTuple2):
                    # for every other wordTuple in the cluster, see if cognate 
                    cognateMatches += 1

            precision = float(cognateMatches) / (len(cluster) -1 )


            allPrecisions.append(precision)


            cogSet1 = goldEvaluator.getCogSetFromTuple(wordTuple1)

            if not cogSet1 is None:
                # if the word belongs to a cogset, see how much of it was found: the recall.
                cognateMatches += 1 # MODIFIED, count itself here?
                numBuddies = len(cogSet1) ##### MODIFIED - 1
                recall = cognateMatches / float(numBuddies)
                allRecalls.append(recall)


    #print("Number of words in clusters total = {0}".format(numWordsInClusters))
    #print("Number of cognate words in non-placed clusters = {0}".format(numOfCognatesNonPlaced))
    #for non in nonPlaced:
    #    print(non)


    recall = sum(allRecalls) / float(len(allRecalls))

    precision = sum(allPrecisions) / float(len(allPrecisions))

    if recall + precision == 0:
        fScore = 0
    else:
        fScore = 2 * recall * precision / (recall + precision)
    #print(allRecalls)
    #print(allPrecisions)
    return recall, precision, fScore


def BUDmini(clustering, truth, mapping, zeroWeightSingletons):
    ''' The clustering input is a dictionary from a cluster label to a list of elements in that cluster.
    The truth is the true clustering
    The mapping, maps an element to its cluster label in the truth, i.e. inverse of the truth
    this method does our modified bCubed, aka BUD for buddies  where elements do not get points for matching with themselves.
    '''

    dontCountPrecision = True # do we count precis
    allRecalls = [] # keep track of the recall of each individual wordTuple
    allPrecisions = [] # keep track of the precision of each individual wordTuple
    allWeights = []
    numNonZeros = 0
    for clusterLabel in sorted(clustering):
        cluster = clustering[clusterLabel]

        if len(cluster) == 1:
            precision = 1.0
            recall = 0
            element1 = cluster[0]
            trueClusterLabel = mapping[element1]
            trueCluster = truth[trueClusterLabel]
            sizeTruth = len(trueCluster)
            isSingleton = (sizeTruth == 1)

            if isSingleton:
                if zeroWeightSingletons:
                    continue
                else:
                    if dontCountPrecision:
                        continue
                    else:
                        allPrecisions.append(precision)
            else:
                allRecalls.append(recall)
                if dontCountPrecision:
                    continue
                else:
                    allPrecisions.append(precision)

            continue

                
        # else: the cluster has more than one element
        for element1 in cluster:
            # each element1 gets its own precision and recall
            truthMatches = 0
            trueClusterLabel = mapping[element1]
            trueCluster = truth[trueClusterLabel]
            sizeTruth = len(trueCluster)

            for element2 in cluster:
                if element1 == element2:
                    # the major modification: don't count matches with themselves
                    continue
                if trueClusterLabel == mapping[element2]:
                    # for every other element in the cluster see if cognate
                    truthMatches += 1

            precision = float(truthMatches) / (len(cluster) - 1)

            isSingleton = (sizeTruth == 1)

            if isSingleton:
                if zeroWeightSingletons:
                    continue
                else:
                    allPrecisions.append(precision)
            else:
                recall = truthMatches / (float(sizeTruth) - 1)
                allRecalls.append(recall)
                allPrecisions.append(precision)
                    

    bcubedRecall = sum(allRecalls)/len(allRecalls)
    bcubedPrecision = sum(allPrecisions)/len(allPrecisions)
    bcubedFScore = 2 * bcubedRecall * bcubedPrecision / (bcubedRecall + bcubedPrecision)

    return bcubedRecall, bcubedPrecision, bcubedFScore



def MUCmini(clustering, truth, mapping, zeroWeightSingletons):
    ''' The clustering input is a dictionary from a cluster label to a list of elements in that cluster.
    The truth is the true clustering
    The mapping, maps an element to its cluster label in the truth, i.e. inverse of the truth
    this method does the MUC metric
    '''

    clusterMapping = createMapping(clustering)
    recall = MUCHelper(clustering, clusterMapping, truth, mapping)

    precision = MUCHelper(truth, mapping, clustering, clusterMapping) # precision is recall formula but treat the truth and the clustering as eachother
    fScore = 2 * recall * precision / (recall + precision)
    return recall, precision, fScore



def createMapping(clustering):
    #given a clustering dictionary, this method returns a dict mapping each element to its cluster label
    clusterMapping = {}
    for label in clustering:
        cluster = clustering[label]
        for element in cluster:
            clusterMapping[element] = label

    return clusterMapping


def MUCHelper(clustering, clusterMapping, truth, mapping):
    numerator = 0
    denominator = 0
    for truthLabel in sorted(truth):
        trueCluster = truth[truthLabel]
        denominator += (len(trueCluster) - 1) # from the formula. the number of links is the number of elements minus 1
        partitionLabels = set() # keep track of the number of partions of this true cluster created by the proposed clustering
        numNonPlacedElements = 0
        for element in trueCluster:
            if element in clusterMapping:
                label = clusterMapping[element]
                partitionLabels.add(label)
            else:
                # if the truth element is not even placed into a cluster, then we consider it its own
                # cluster, and therefore it adds to the number of partitions created by the clustering
                numNonPlacedElements += 1

        numPartitions = len(partitionLabels) + numNonPlacedElements # the number of labels and the number of non placed elements
        numerator += len(trueCluster) - numPartitions 

    #print()
    return float(numerator) / denominator



def MUC(clustering, goldEvaluator):

    #print("Number of clusters = {0}".format(len(clustering)))

    truth = goldEvaluator.numToCognateSet
    truthMapping = createMapping(truth)
    clusterMapping = createMapping(clustering)

    #print(len(clusterMapping))
    #print(len(truthMapping))
    fillMappingWithNonGoldWords(truthMapping, clusterMapping) # this makes sure every word in the cluster mapping is also in the truth mapping, as a singleton
    #print(len(truthMapping))

    recall = MUCHelper(clustering, clusterMapping, truth, truthMapping)
    precision = MUCHelper(truth, truthMapping, clustering, clusterMapping) # precision is recall formula but treat the truth and the clustering as eachother

    if recall + precision == 0:
        fScore = 0
    else:
        fScore = 2 * recall * precision / (recall + precision)
    return recall, precision, fScore



def fillMappingWithNonGoldWords(truthMapping, clusterMapping):
    # the cluster mapping will contain elements that the truth mapping does not. This will cause an error when calculating
    # MUC precision, so we need to add those elements to the truth mapping with a unique cluster label
    newLabel = -1
    for element in clusterMapping:
        if element in truthMapping:
            #print("original mapping {0}".format(truthMapping[element]))
            continue

        truthMapping[element] = newLabel
        #print("new label {0}".format(truthMapping[element]))
        newLabel -= 1


def clusterPurity(clustering, goldEvaluator):

    #print("Number of clusters = {0}".format(len(clustering)))
    numWordsInClusters = 0
    matches = 0

    for clusterLabel in sorted(clustering):
        cluster = clustering[clusterLabel]
        numWordsInClusters += len(cluster)
        trueCogNums = defaultdict(int)

        for wordTuple in cluster:
            # first loop through to find the majority truth cluster
            cogNum = goldEvaluator.getCogNumFromTuple(wordTuple)
            if not cogNum is None:
                trueCogNums[cogNum] += 1 

        if len(trueCogNums) == 0:
            matches += 1 # if no word was in a gold set, then we say that the max overlap is 1
        else:
            matches += max(trueCogNums.values())

    #print("matches = {0}".format(matches))
    purity = float(matches)/ numWordsInClusters
    return purity



def clusterPurityNoSingletons(clustering, goldEvaluator):
    # this is purity but does not count singletons
    # this gives an idea of how pure the actual clusters are

    numWordsInClusters = 0
    matches = 0

    for clusterLabel in sorted(clustering):
        cluster = clustering[clusterLabel]
        if len(cluster) == 1:
            # don't want to include the purity of a singleton word
            continue

        numWordsInClusters += len(cluster)
        trueCogNums = defaultdict(int)

        for wordTuple in cluster:
            # first loop through to find the majority truth cluster
            cogNum = goldEvaluator.getCogNumFromTuple(wordTuple)
            if not cogNum is None:
                trueCogNums[cogNum] += 1 

        if len(trueCogNums) == 0:
            matches += 1 # if no word was in a gold set, then we say that the max overlap is 1
        else:
            matches += max(trueCogNums.values())


    #print("matches = {0}".format(matches))
    purity = float(matches)/ numWordsInClusters
    return purity




def purityMini(clustering, truth, mapping, zeroWeightSingletons):
    ''' purity metric as defined in Hall and Klein 2011 '''

    doNotCountNonPlaced = False # this flag skips those clusters with only one element, i.e. "nonplaced" elements

    total = 0
    matches = 0

    for clusterLabel in sorted(clustering):
        cluster = clustering[clusterLabel]
        #print(cluster)
        trueLabels = defaultdict(int)


        if len(cluster) == 1 and doNotCountNonPlaced:
            continue

        for element in cluster:
            # first loop through to find the majority truth cluster
            trueClusterLabel = mapping[element]
            trueLabels[trueClusterLabel] += 1 

        maxLabel = max(trueLabels.keys(), key=(lambda key: trueLabels[key]))
        #print("maxLabel = {0}".format(maxLabel))

        for element in cluster:
            #print("element = {0}".format(element))
            total += 1
            trueClusterLabel = mapping[element]
            if trueClusterLabel == maxLabel:
                matches += 1
                #print("match")
            else:
                pass
                #print("no match")
          
    recall = None
    print("matches = {0}, total = {1}".format(matches, total))
    purity = float(matches)/ total
    fScore = None
    return recall, purity, fScore


def pairWise(clustering, goldEvaluator):
    # given a clustering and a GoldEvaluator object, this method calculates the 
    # pairwise recall, precision, and FScore of the clustering. Using the GoldEvaluator's numToCognateSet as
    # the truth
    truth = goldEvaluator.numToCognateSet
    return pairwiseGeneral(clustering, truth)


def pairwiseMini(clustering, truth, mapping, zeroWeightSingletons):
    ''' The clustering input is a dictionary from a cluster label to a list of elements in that cluster.
    The truth is the true clustering
    The mapping, maps an element to its cluster label in the truth, i.e. inverse of the truth
    this method does pairwise comparisons
    '''
    return pairwiseGeneral(clustering, truth)


def pairwiseGeneral(clustering, truth):
    truePairs = createPairs(truth)

    #proposedPairs = createPairs(clustering)
    #overlapPairs = truePairs & proposedPairs
    #overlap = len(overlapPairs)
    #numProposed = len(proposedPairs)
    #recall = len(truePairs & proposedPairs) / float(len(truePairs))
    #precision = len(truePairs & proposedPairs) / float(len(proposedPairs))


    overlap, numProposed = countOverlapAndProposed(truePairs, clustering)
    recall = overlap / float(len(truePairs))
    precision = overlap / float(numProposed)

    #print("overlap = {0}".format(overlap))
    #print("numProposed = {0}".format(numProposed))
    #print("precision = {0}".format(precision))
    if recall + precision == 0:
        fScore = 0
    else:
        fScore = 2 * recall * precision / (recall + precision)
    return recall, precision, fScore


def countOverlapAndProposed(truePairs, clustering):
    # this doesn't create a set for all the proposed pairs. this would possibly take too much memory,
    # at least in the case of the Max Recall baseline of all words in one cluster.
    # instead, look at the pairs and then see on the fly whether they are in the truePairs or not and keep track
    overlap = 0
    numProposed = 0
    for label in sorted(clustering):
        cluster = sorted(clustering[label]) # need to sort so always create pairs in the same order in truth or proposed clustering
        for i, element1 in enumerate(cluster):
            #if i % 3000 == 50:
            #    print("i = {0}".format(i))
            j = i+1
            while j < len(cluster):
                element2 = cluster[j]
                pair = (element1, element2)
                if pair in truePairs:
                    overlap += 1
                numProposed += 1
                j += 1
    return overlap, numProposed


def createPairs(clustering):
    pairs = set()
    for label in clustering:
        cluster = sorted(clustering[label]) # need to sort so always create pairs in the same order in truth or proposed clustering
        for i, element1 in enumerate(cluster):
            #if i % 500 == 50:
            #    print("i = {0}".format(i))
            j = i+1
            while j < len(cluster):
                element2 = cluster[j]
                pair = (element1, element2)
                pairs.add(pair)
                j += 1
    return pairs


if __name__ == "__main__":
    from collections import defaultdict
    testClusters = defaultdict(list)


    def addToCluster(clusters, clusterLabel, wordString):
        ''' takes a clusters dict and a label and a string acc\tword\tdefn, splits and adds to dict '''
        wordTuple = wordString.split('\t')
        clusters[clusterLabel].append(wordTuple)


    addToCluster(testClusters, "a", "C\taːčimeːw\the tells of him")
    addToCluster(testClusters, "a", "M\taːčemæw\the tells about him")
    addToCluster(testClusters, "a", "F\taːčimeːwa\the tells him")
    addToCluster(testClusters, "a", "M\taːčemow\the narrates, reports an event")
    addToCluster(testClusters, "a", "M\taːčemow\the narrates, reports an event")


    addToCluster(testClusters, "b", "C\taːčimostaːtoːwak\tthey narrate to each other")
    addToCluster(testClusters, "b", "M\taːčemiːqtatowak\tthey tell each other stories")
    addToCluster(testClusters, "b", "F\taːčimowa\the narratesss")

    goldEval = GoldEvaluator("../DataFiles/GoldSetsAlgonquian.txt")

    #recall, precision, fscore = bCubed(testClusters, goldEval)
    #print("recall = {0}, precision = {1}, fscore = {2}".format(recall, precision, fscore))




    def createTruthAndMapping1():
        truth = {}
        mapping = {}
        truth['l1'] = ['s1']
        mapping['s1'] = 'l1'
        truth['l2'] = ['s2']
        mapping['s2'] = 'l2'
        truth['l3'] = ['s3']
        mapping['s3'] = 'l3'
        truth['l4'] = ['s4']
        mapping['s4'] = 'l4'
        truth['l5'] = ['s5']
        mapping['s5'] = 'l5'
        truth['l6'] = ['s6']
        mapping['s6'] = 'l6'
        truth['l7'] = ['s7']
        mapping['s7'] = 'l7'
        truth['l8'] = ['s8']
        mapping['s8'] = 'l8'


        truth['l9'] = ['a1', 'a2']
        mapping['a1'] = 'l9'
        mapping['a2'] = 'l9'

        truth['l10'] = ['b1', 'b2', 'b3']
        mapping['b1'] = 'l10'
        mapping['b2'] = 'l10'
        mapping['b3'] = 'l10'

        truth['l11'] = ['c1', 'c2', 'c3', 'c4', 'c5']
        mapping['c1'] = 'l11'
        mapping['c2'] = 'l11'
        mapping['c3'] = 'l11'
        mapping['c4'] = 'l11'
        mapping['c5'] = 'l11'
        return truth, mapping


    def createTruthAndMapping2():
        truth = {}
        mapping = {}
        truth['l1'] = ['s1']
        mapping['s1'] = 'l1'
        truth['l2'] = ['s2']
        mapping['s2'] = 'l2'
        truth['l3'] = ['s3']
        mapping['s3'] = 'l3'
        truth['l4'] = ['s4']
        mapping['s4'] = 'l4'
        truth['l5'] = ['s5']

        truth['l9'] = ['a1', 'a2']
        mapping['a1'] = 'l9'
        mapping['a2'] = 'l9'

        truth['l10'] = ['b1', 'b2', 'b3']
        mapping['b1'] = 'l10'
        mapping['b2'] = 'l10'
        mapping['b3'] = 'l10'
        return truth, mapping



    def test1(truth, mapping, zeroWeightSingletons, evalMetric):
        print("high precision clustering: almost each in own cluster. One true pairing.")
        clustering = {}
        clustering[-1] = ["c4", "c5"] # these two put together
        clusterLabel = 0
        for element in mapping:
            if element in ["c4", "c5"]:
                continue
            clustering[clusterLabel] = [element]
            clusterLabel += 1
        #print(clustering)
        recall, precision, fscore = evalMetric(clustering, truth, mapping, zeroWeightSingletons)
        printResults(recall, precision, fscore)


    def test2(truth, mapping, zeroWeightSingletons, evalMetric):
        print("high recall clustering. All in one cluster.")
        clustering = {}
        clustering['c1'] = []
        for element in mapping:
            clustering['c1'].append(element)
        recall, precision, fscore = evalMetric(clustering, truth, mapping, zeroWeightSingletons)
        printResults(recall, precision, fscore)


    def test3(truth, mapping, zeroWeightSingletons, evalMetric):
        print("A decent clustering")
        clustering = {}
        clustering['c1'] = ['a1', 'a2', 's1', 's2', 'b1']
        clustering['c2'] = ['b2', 'b3']
        clustering['c3'] = ['c1', 'c2', 'c3', 's3', 's4', 's5']
        clustering['c4'] = ['s6']
        clustering['c5'] = ['s7']
        clustering['c6'] = ['s8']
        clustering['c7'] = ['c4']
        clustering['c8'] = ['c5']

        recall, precision, fscore = evalMetric(clustering, truth, mapping, zeroWeightSingletons)
        printResults(recall, precision, fscore)


    def test4(truth, mapping, zeroWeightSingletons, evalMetric):
        print("a good clustering")
        clustering = {}
        clustering['c1'] = ['a1', 'a2', 's1']
        clustering['c2'] = ['b1', 'b2', 'b3', 's4']
        clustering['c3'] = ['c1', 'c2', 'c3', 's2', 's3']
        clustering['c4'] = ['s6']
        clustering['c5'] = ['s7']
        clustering['c6'] = ['s8']
        clustering['c7'] = ['s5']

        clustering['c8'] = ['c5']
        #clustering['c9'] = ['s4']
        clustering['c10'] = ['c4']
        
        recall, precision, fscore = evalMetric(clustering, truth, mapping, zeroWeightSingletons)
        printResults(recall, precision, fscore)


    def test6(truth, mapping, zeroWeightSingletons, evalMetric):
        print("no singleton clustering")
        clustering = {}
        clustering['c1'] = ['a1', 'a2', 'b1', 'b2', 'b3', 'c1', 'c2', 'c3', 'c4', 'c5']
        clustering['c2'] = ['s1']
        clustering['c3'] = ['s2']
        clustering['c8'] = ['s3']
        clustering['c9'] = ['s4']
        clustering['c4'] = ['s6']
        clustering['c5'] = ['s7']
        clustering['c6'] = ['s8']
        clustering['c7'] = ['s5']

        #print(truth)
        #print(clustering)
        recall, precision, fscore = evalMetric(clustering, truth, mapping, zeroWeightSingletons)
        printResults(recall, precision, fscore)


    def test5(truth, mapping, zeroWeightSingletons, evalMetric):
        print("the truth used as clustering")
        clustering = truth
        recall, precision, fscore = evalMetric(clustering, truth, mapping, zeroWeightSingletons)
        printResults(recall, precision, fscore)

    def printResults(r, p, f):
        print("recall = {0:.3f}, precision = {1:.3f}, fscore = {2:.3f}\n".format(r, p, f))
        
    truth, mapping = createTruthAndMapping1()
    zeroWeightSingletons = False

    if zeroWeightSingletons:
        print("Zero weight singletons")
    else:
        print("Full weight singletons")



    evalMetric = MUCmini # change this to different function name to use
    #metrics = [MUCmini, BUDmini, purityMini, pairwiseMini, bCubedMini]
    metrics = [pairwiseMini]
    for evalMetric in metrics:
        print(evalMetric)
        test5(truth, mapping, zeroWeightSingletons, evalMetric)
        test2(truth, mapping, zeroWeightSingletons, evalMetric)
        test1(truth, mapping, zeroWeightSingletons, evalMetric)
        test3(truth, mapping, zeroWeightSingletons, evalMetric)
        test4(truth, mapping, zeroWeightSingletons, evalMetric)
        test6(truth, mapping, zeroWeightSingletons, evalMetric)
    
