#!/usr/bin/env python3


''' this file contains the classes used to read in an example pair file that looks like

+[\tab]word1[\tab]word2
-[\tab]word1[\tab]word2
-[\tab]word1[\tab]word2
+[\tab]word1[\tab]word2
....

and featurizes each pair and writes the featurized output to file for svm-light


if --training is specified then a feature dictionary is created and written to file
if --testing is specified then the given feature dictionary is read from file

'''



from SubstringFeaturizer import SubstringFeaturizerForSVMLight
from FeatureRunner import SubstringFeatureRunner

import time
from multiprocessing import Process, Pipe

class RunnerForExamples(SubstringFeatureRunner):
    
    def __init__(self, examplePairsFile, outputFeaturesFile, featurizer, featureDictFileName, trainingFlag):
        super().__init__(outputFeaturesFile, featurizer)
        self.featureDictFileName = featureDictFileName
        self.examplePairsFile = examplePairsFile
        self.trainingFlag = trainingFlag

    def displayCurrentProgress(self, startTime, currentTime, currentIndex):
        seconds = currentTime - startTime
        minutes = seconds/60.0
        hours = minutes/60.0
        sys.stderr.write("\033[F")
        sys.stderr.write("Featurizing example {0} / {1}; current minutes = {2:.2f}m, current hours = {3:.2f}h\n".format(currentIndex, self.numExamples, minutes, hours))


    def run(self, sender=None):
        self.numExamples = sum(1 for line in open(self.examplePairsFile))
        
        if sender is None:
            sys.stderr.write("Featurizing file: {0}\n\n".format(self.examplePairsFile))
        with open(self.examplePairsFile) as file:
            t1 = time.clock()
            active = True
            for i, line in enumerate(file):
                t2 = time.clock()
                if sender is None: 
                    self.displayCurrentProgress(t1, t2, i)
                else:
                    sender.send((i, self.numExamples, self.examplePairsFile, active))

                line = line.strip()
                classification, word1, word2 = line.split()
                if classification == "+":
                    classification = 1
                else:
                    classification = -1

                self.featurizeGivenPair(word1, word2, classification)


            if sender is None:
                sys.stderr.write("The number of total training features is {0}\n".format(len(self.featurizer.featureDict)))            
                if not self.trainingFlag:
                    sys.stderr.write("The number of total testing features is {0}\n".format(len(self.featurizer.allTestingFeatures)))
                    sys.stderr.write("The number of testing only features is {0}\n".format(len(self.featurizer.testingOnlyFeatures)))
                    sys.stderr.write("The number of training features seen in testing is {0}\n".format(len(self.featurizer.seenTrainingFeatures)))
                    #self.featurizer.printTestingOnlyFeatures()
            else:
                # send the last message to the receiver that we are finished
                active = False
                sender.send((self.numExamples, self.numExamples, self.examplePairsFile, active))

if __name__ == "__main__":

    import optparse
    import sys

    parser = optparse.OptionParser()
    parser.add_option('-i', action='store', dest='inputPairsFile', help="the input name for example pairs file, i.e. the pairs to featurize.")
    parser.add_option('-o', action='store', dest='outputFile', help="the output file name for the features. If none given, then prints them.", default=None)
    parser.add_option('-f', action='store', dest='featureDictFile', help="the output(or input) name for feature dictionary file")
    parser.add_option('-m', action='store', dest='maxSubstringLength', help="the maximum substring length, default = 3", default=3)
    parser.add_option('-s', action='store', dest='substitutionCost', help="the substitutionCost for the alignment algorithm. default = 2.", default=2)

    parser.add_option('--training', action='store_true', dest='training', help="use if training, and hence will write to the feature dict file.", default=False)
    parser.add_option('--testing', action='store_true', dest='testing', help="use if testing, and hence will read from the feature dict file.", default=False)


    # the following arguments are used when running in parallel
    # since multiple files will be read in and writed out, we need to just give the paths to these directories
    # it is assumed that the names of the files follow a certain format (see createJobsForEachLanguagePair function)
    parser.add_option('--parallelize', action='store_true', dest='parallelize', help="flag if want to use automatic Python parallelization.", default=False)
    parser.add_option('--inputPath', action='store', dest='inputPath', help="the path to where the input files are being read from (only used if parallelize is turned on)")
    parser.add_option('--outputPath', action='store', dest='outputPath', help="the path to where the output features should be created (only used if parallelize is turned on)")
    parser.add_option('--featureDictPath', action='store', dest='featureDictPath', help="the path to where the feature dicts are being read from (only used if parallelize is turned on)")
    parser.add_option('--family', action='store', dest='family', help="the language family, (only used if parallelize is turned on)", default="algonquian")

    options, args = parser.parse_args()


    if (options.inputPairsFile is None or options.outputFile is None) and not options.parallelize:
        sys.stderr.write("Must provide input and output file names if not running in parallel!\n")
        parser.print_help()
        exit(-1)


    if (options.training and options.testing) or (not options.training and not options.testing):
        sys.stderr.write("Must indicate exactly one of training or testing!\n")
        parser.print_help()
        exit(-1)


    if options.testing and options.featureDictFile is None and not options.parallelize:
        sys.stderr.write("Must provide a feature dict file if testing!\n")
        parser.print_help()
        exit(-1)

    if (options.outputPath is None or options.inputPath is None or options.featureDictPath is None) and options.parallelize:
        sys.stderr.write("Must provide the file paths when parallelizing!\n")
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


    def createJobsForEachLanguagePair(langTuples, inputPath, outputPath, featureDictPath):
        # for each pair of languages in the langTuples list, a process is created that will featurize the given pair
        # the receivers list contains a list of Pipes, able to get information from the jobs as they run
        jobs = []
        receivers = []
        for i, tuple1 in enumerate(langTuples):
            acc1, lang1 = tuple1
            for j in range(i, len(langTuples)):
                acc2, lang2 = langTuples[j]
                #lang1 = "fox"
                #lang2 = "oji"
                inputPairsFile = "{0}/no_definition_pairs_{1}_{2}.txt".format(inputPath, lang1, lang2)
                featureDictFile = "{0}/feature_dict_{1}_{2}.txt".format(featureDictPath, lang1, lang2)
                outputFile = "{0}/substring_feature_values_{1}_{2}.txt".format(outputPath, lang1, lang2)
                receiver, sender = Pipe() # the pipe is used to get information from each process regarding its progress
                p = Process(target=featurizeFile, args=(sender, inputPairsFile, featureDictFile, outputFile, options.training, options.maxSubstringLength, options.substitutionCost))
                receivers.append(receiver)
                p.start()
                jobs.append(p)

        return jobs, receivers


    def featurizeFile(sender, inputPairsFile, featureDictFile, outputFile, trainingFlag, maxSubstringLength, substitutionCost):
        featurizer = SubstringFeaturizerForSVMLight(maxSubstringLength, trainingFlag, substitutionCost)
        with RunnerForExamples(inputPairsFile, outputFile, featurizer, featureDictFile, trainingFlag) as exampleRunner:
            exampleRunner.run(sender)


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
                while receiver.poll():  # check if the receiver has received a message
                    # we loop so that we always check the most recent status report
                    status = receiver.recv()
                    active = status[3]
                    if not active:
                        receiverIndicesToDelete.append(i)
                        break


                if status is not None:
                    current, total, fileName, active = status
                    statusDict[fileName] = status

            # now print out each status
            for key in sorted(list(statusDict.keys())):
                status = statusDict[key]
                current, total, fileName, active = status            
                if active:
                    finishedFlag = ""
                else:
                    finishedFlag = "Complete!"
                sys.stderr.write("{2}: {0} / {1}\t\t{3}\n".format(current, total, fileName, finishedFlag))
            
            #finally, remove the receivers that are finished. Must do it in reverse order of index
            for index in sorted(receiverIndicesToDelete, reverse=True):
                receivers[index].close()
                del receivers[index]



    if options.parallelize:
        # first, determine which languages we are looking at, based on the inputted language family
        langTuples = getLanguageTuplesFromFamily(options.family)

        # then featurize each language pair in parallel. start a new job for each pair.
        jobs, receivers = createJobsForEachLanguagePair(langTuples, options.inputPath, options.outputPath, options.featureDictPath) 

        # now we just loop and get the status from each job. displays the progress of each input file to stderr until all jobs are done.
        displayProgressForAllJobs(receivers)

        #finally, terminate all jobs
        for job in jobs:
            job.terminate()

    else:
        # if not parallelizing, then just featurize once, with the given language pair
        sender = None # sender is only used when running in parallel
        featurizeFile(sender, options.inputPairsFile, options.featureDictFile, options.outputFile, options.training, options.maxSubstringLength, options.substitutionCost)


