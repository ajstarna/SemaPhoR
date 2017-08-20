#!/usr/bin/env python3

'''
this script reads in the language dictionaires from two languages and their correponding pairwise alignment scores.
for the pairs that exceed the given threshold, creates the features and outputs the pair and the feature values to the two respective output files

- can also be ran in parallel with --parallel, and this creates the features for all lang pairs at the same time.
- when ran in parallel, only one featurizer is created, so the large word2vec model only needs to be read into memory once

'''

import sys
import time

from multiprocessing import Process, Pipe

from LanguageDictParser import AlgonquianLanguageDictParser
from alignmentFeatures import lookUpWordPairStrict


from FeatureRunner import GeneralFeatureRunner
from GeneralFeaturizer import GeneralFeaturizer
from ExampleCreator import ExampleCreator



class RunnerForLangDicts(GeneralFeatureRunner):

    def __init__(self, outputPairsFile, outputFeaturesFile, featurizer, family,  acc1, acc2, threshold, readFromThreshold):
        super().__init__(outputFeaturesFile, featurizer)
        self.outputPairsFile = outputPairsFile
        self.acc1 = acc1
        self.acc2 = acc2
        self.threshold = threshold
        self.readFromThreshold = readFromThreshold        

        if family == "totonac":
            ldp = TotonacLanguageDictParser()
        elif family == "algonquian":
            ldp = AlgonquianLanguageDictParser()
        else:
            sys.stderr.write("unknown language family!\n")
            exit(-1)

        self.dict1 = ldp[self.acc1]
        self.dict2 = ldp[self.acc2]
        self.words1 = sorted(list(self.dict1.keys()))
        self.words2 = sorted(list(self.dict2.keys()))


    def displayCurrentProgress(self, startTime, currentTime, currentIndex):
        seconds = currentTime - startTime
        minutes = seconds/60.0
        hours = minutes/60.0
        sys.stderr.write("\033[F")
        sys.stderr.write("{0} / {1} dict1 words created; Time so far is {2:.2f}s " 
                         "= {3:.2f}m = {4:.2f}h\n".format(currentIndex, len(self.words1), seconds, minutes, hours))


    def run(self, sender=None):
        if sender is None:
            sys.stderr.write("looking at {0} and {1}\n".format(self.acc1, self.acc2))
            sys.stderr.write("size of dict1 = {0}\n".format(len(self.dict1)))
            sys.stderr.write("size of dict2 = {0}\n\n".format(len(self.dict2)))

        classification = -1 # the classification of each featurize pair is negative

        with ExampleCreator(self.outputPairsFile) as pairWriter:
            # this will have an instance of an example creator, since we want to write the example pairs that
            # pass the threshold to be featurized
            t1 = time.time()
            active = True
            for i, uni1 in enumerate(self.words1):
                t2 = time.time()
                if sender is None: 
                    self.displayCurrentProgress(t1, t2, i)
                else:
                    sender.send((i, len(self.words1), self.acc1, self.acc2, active))
                asjp1 = self.getASJP(uni1)
                aline1 = self.getALINE(uni1)

                for def1 in self.dict1[uni1]:
                    cleanedDef1 = self.getClean(def1)
                    if cleanedDef1 == "":
                        continue

                    if self.acc1 == self.acc2:
                        startIndex = i + 1
                    else:
                        startIndex = 0

                    for j in range(startIndex, len(self.words2)):
                        uni2 = self.words2[j]
                        asjp2 = self.getASJP(uni2)
                        aline2 = self.getALINE(uni2)

                        if self.belowThreshold(aline1, aline2):
                            continue

                        for def2 in self.dict2[uni2]:
                            cleanedDef2 = self.getClean(def2)
                            if cleanedDef2 == "":
                                continue
                            self.featurizeGivenPair(uni1, uni2, asjp1, asjp2, aline1, aline2, def1, def2, 
                                                    cleanedDef1, cleanedDef2, self.acc1, self.acc2, classification)
                            
                            pairWriter.writeNegativePair((self.acc1, uni1, def1), (self.acc2, uni2, def2))

            if sender is not None:
                # send the last message to the receiver that we are finished
                active = False
                sender.send((len(self.words1), len(self.words1), self.acc1, self.acc2, active))    
                        
    def belowThreshold(self, aline1, aline2):
        # given two words in ALINE format, we look the pair up in the alignment dictinoary. 
        # based on whether the pair is found in the dictionary, what the returned score is, and whether we are looking in a threshold alignment file,
        # i.e. a file that only include scores for pairs that exceed a given threshold to begin with
        score, alignedCons = lookUpWordPairStrict(self.featurizer.alignmentFeaturesDict, aline1, aline2)
        if score is None:
            if self.readFromThreshold:
                return True
            else:
                # this shouldn't happen. All scores should be precomputed and found in the read-in binary file
                sys.stderr.write("couldn't find pair: {0}, {1}\n".format(aline1, aline2))
                exit(-1)
        if score <= self.threshold:
            if self.readFromThreshold:
                # sanity check
                # if get to here then score was non-None and less than threshold, even though we are reading from the specific threshold file
                sys.stderr.write("score below threshold! {0}, {1}\n".format(aline1, aline2))
                exit(-1)
            else:
                return True
        else:
            return False





if __name__ == "__main__":

    import optparse
    
    parser = optparse.OptionParser()
    parser.add_option('-f', action='store', dest='outputFeaturesName', help="the output name for features.")
    parser.add_option('-p', action='store', dest='outputPairsName', help="the output name for pairs.")

    parser.add_option('--l1', action='store', dest='acc1', help="the language Acc for first language (ex. C,F,M,O)")
    parser.add_option('--l2', action='store', dest='acc2', help="the language Acc for second language (ex. C,F,M,O)")
    parser.add_option('--lang', '-l', action='store', dest='defnLanguage', help="the language of the definitions in the example pairs. default = en", default="en")
    parser.add_option('--family', action='store', dest='family', help="the language family", default="algonquian")

    parser.add_option('-a', action='store', dest='alignmentFeaturesFile', help="the alignment feature file.")

    parser.add_option('-t', action='store', dest='threshold', help="the nusimil score threshold for sending pair to featurizer. default = 0.35", default=0.35)
    parser.add_option('-r', action='store_true', dest='readFromThreshold', help="flag to say if reading from an alignment file with other pairs passing the threshold", default=False)


    # to turn off specific feature(s)
    parser.add_option('-u', action='store', dest='UseFeatureNumbers', help="feature numbers to use. ex: 1,2,9,13")
    parser.add_option('-y', action='store', dest='UseFeatureType', help="feature type to use. ex: 'surface' or 'word2Vec'")



    # when featurizing in parellel
    parser.add_option('--parallelize', action='store_true', dest='parallelize', help="flag if want to use automatic Python parallelization.", default=False)
    parser.add_option('--outputPath', action='store', dest='outputPath', help="the path to where the output features and pairs files should be created (only used if parallelize is turned on)")
    parser.add_option('--alignmentPath', action='store', dest='alignmentPath', help="the path to where the alignment feature files are found (only used if parallelize is turned on)")

    options, args = parser.parse_args()

    if (options.outputFeaturesName is None or options.outputPairsName is None) and not options.parallelize:
        sys.stderr.write("Must provide the output name if not running in parallel!\n")
        parser.print_help()
        exit(-1)
        

    if (options.acc1 is None or options.acc2 is None) and not options.parallelize:
        sys.stderr.write("Must provide the language accronyms if not running in parallel!\n")
        parser.print_help()
        exit(-1)

    if (options.outputPath is None or options.alignmentPath is None) and options.parallelize:
        sys.stderr.write("Must provide the output and alignment paths when parallelizing!\n")
        parser.print_help()
        exit(-1)




    def getLanguageTuplesFromFamily(family):
        # given a language family: totonac or algonquian, returns a list of langTuples, where each tuple is (acc, language), e.x. ('C', 'cree')
        if family == "totonac":
            langs = ["apapantilla", "coatepec", "coyutla", "filomenomata", 
                     "misantla", "papantla", "pisaflores", 
                     "tlachichilco", "uppernecaxa", "zapotitlan"]
            accs = ["A", "C", "Y", "F", "M", "P", "I", "T", "U", "Z"]
        elif family == "algonquian":
            langs = ['cree','fox', 'meno', 'oji']
            accs = ['C', 'F', 'M',  'O']
        else:
            sys.stderr.write("unknown language family!\n")
            exit(-1)
        langTuples = list(zip(accs, langs))
        return langTuples


    def addAlignmentFeaturesToFeaturizer(featurizer, langTuples, alignmentPath):
        # given a featurizer object, a langTuples list, and the path to where alignment feature files are found,
        # reads each file for pairs of languages and adds the scores to the featurizer
        # this assumes a certain format for the alignment features files
        for i, tuple1 in enumerate(langTuples):
            acc1, lang1 = tuple1
            for j in range(i, len(langTuples)):
                acc2, lang2 = langTuples[j]
                alignmentFeaturesFile = "{0}/alignment_features_{1}_{2}_0.35Threshold.bin".format(alignmentPath, lang1, lang2)
                featurizer.readAdditionalAlignmentFile(alignmentFeaturesFile)

    def featurizeFile(sender, outputFeaturesFile, outputPairsFile, family, small, acc1, acc2, threshold, readFromThreshold):
        # the function that is given to each job (or called once if we are not parallelizing)
        # a Runner is created with the input parameters, and the features and output pairs are written to the given file names
        with RunnerForLangDicts(outputFeaturesFile, outputPairsFile, family, small, acc1, acc2, threshold, readFromThreshold) as runner:
            runner.run(sender)

    def createJobsForEachLanguagePair(featurizer, langTuples, family, outputPath, threshold, readFromThreshold):
        # for each pair of languages in the langTuples list, a process is created that will featurize the given pair
        # the receivers list contains a list of Pipes, able to get information from the jobs as they run
        jobs = []
        receivers = []
        for i, tuple1 in enumerate(langTuples):
            acc1, lang1 = tuple1
            for j in range(i, len(langTuples)):
                acc2, lang2 = langTuples[j]
                outputFeaturesFile = "{0}/feature_values_{1}_{2}.txt".format(outputPath, lang1, lang2)
                outputPairsFile = "{0}/word_pairs_{1}_{2}.txt".format(outputPath, lang1, lang2)
                receiver, sender = Pipe() # the pipe is used to get information from each process regarding its progress
                p = Process(target=featurizeFile, args=(sender, outputPairsFile, outputFeaturesFile, featurizer, family, acc1, acc2, threshold, readFromThreshold))
                receivers.append(receiver)
                p.start()
                jobs.append(p)
        return jobs, receivers


    def displayProgressForAllJobs(receivers):
        # this function gets status reports from each receiver about its corresponding job, and displays the progress info to stderr
        CURSOR_UP_ONE = '\x1b[1A'
        statusDict = {} # keeps the currrent status for given language pairs. 
        # the status dict gets updated when the receiver gets new messages. Once a job is done, the last status remains forever in the dict
        startTime = time.time()
        sys.stderr.write("\n\n")
        while len(receivers) > 0: # once a job is finished, the receiver will be removed from the list, so we loop while there are still some in the list

            # reset the cursor for the next time through the loop
            for _ in range(len(statusDict) + 1): # backtrack the length of the status dict + 1 for the time-report line
                sys.stderr.write(CURSOR_UP_ONE)

            currentTime = time.time()
            seconds = currentTime - startTime
            minutes = seconds/60.0
            hours = minutes/60.0
            sys.stderr.write("Time for featurizing = {0:.2f}s = {1:.2f}m = {2:.2f}h\n".format(seconds, minutes, hours))

            time.sleep(1)
            # check each reveiver for a status report, and if they are finished, then remove them from the receivers list
            receiverIndicesToDelete = []
            for i, receiver in enumerate(receivers):
                status = None
                while receiver.poll(): # check if the receiver has received a message
                    # we loop so that we always check the most recent status report
                    status = receiver.recv()
                    active = status[4]
                    if not active:
                        receiverIndicesToDelete.append(i)
                        break

                if status is not None:
                    current, total, acc1, acc2, active = status
                    statusDict[(acc1,acc2)] = status

            # now print out each status
            for key in sorted(list(statusDict.keys())):
                status = statusDict[key]
                current, total, acc1, acc2, active = status            
                if active:
                    finishedFlag = ""
                else:
                    finishedFlag = "Complete!"
                sys.stderr.write("{2} and {3}: {0} / {1}\t\t{4}\n".format(current, total, acc1, acc2, finishedFlag))


            #finally, remove the receivers that are finished. Must do it in reverse order of index
            for index in sorted(receiverIndicesToDelete, reverse=True):
                receivers[index].close()
                del receivers[index]

            
    # determine the feature numbers to use in the featurizer, based on arguments
    if options.UseFeatureNumbers is not None:
        stringNumbers =  options.doNotUseFeatureNumbers.split(",")
        try:
            featureNumbersToUse = [int(num) for num in stringNumbers]
        except:
            sys.stderr.write("Invalid feature numbers provided as argument!\n")
            exit(-1)
    elif options.UseFeatureType is not None:
        featureNumbersToUse = options.UseFeatureType
    else:
        # if no feature numbers specified, then use a default featurizer
        featureNumbersToUse = GeneralFeaturizer.allFeatures

    featurizer = GeneralFeaturizer(options.defnLanguage, options.alignmentFeaturesFile, featureNumbersToUse)


    threshold = float(options.threshold)
    t1 = time.time()
    if options.parallelize:
        # first, determine which languages we are looking at, based on the inputted language family
        langTuples = getLanguageTuplesFromFamily(options.family)

        # next, read in all the alignment features into the featurizer for each pair of langs
        addAlignmentFeaturesToFeaturizer(featurizer, langTuples, options.alignmentPath)

        # then featurize each language pair in parallel. start a new job for each pair.
        jobs, receivers = createJobsForEachLanguagePair(featurizer, langTuples, options.family, options.outputPath, threshold, options.readFromThreshold)

        # now we just loop and get the status from each job. displays the progress of each language pair to stderr until all jobs are done.
        displayProgressForAllJobs(receivers)

        #finally, terminate all jobs
        for job in jobs:
            job.terminate()

    else:
        # if not parallelizing, then just featurize once, with the given language pair
        sender = None # sender is only used when running in parallel
        featurizeFile(sender, options.outputPairsName, options.outputFeaturesName, featurizer, options.family, options.acc1, options.acc2, threshold, options.readFromThreshold)


    t2 = time.time()
    seconds = t2- t1
    minutes = seconds/60.0
    hours = minutes/60.0
    sys.stderr.write("Time to run was {0:.2f}s = {1:.2f}m = {2:.2f}h\n".format(seconds, minutes, hours))
    #sys.stderr.write("Feel free to exit program, if it is hanging.\n")

