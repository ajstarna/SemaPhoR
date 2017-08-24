#!/usr/bin/env python3

# this script runs the necessary files to train the specific substring models for each Algonquian language pair.
# use the -p argument for parallelizing. Otherwise, it is run sequential and takes longer.

import handleCommand

BASELINES_PATH = "../Output/Baselines"
OUTPUT_PATH = "../Output/SubstringModels"


langTuples = [("cree", "C"), ("fox", "F"), ("meno", "M"), ("oji", "O")]

def createSubstringTrainingPairs():
    # need to do for all possible language combos
    for i, langTuple in enumerate(langTuples):
        
        lang1, acc1 = langTuple
        for j in range(i, len(langTuples)):
            otherTuple = langTuples[j]
            lang2, acc2 = otherTuple
            trainCreateCommand = ("./createExamplePairsFromInputSets.py --defSets -i {0}/FirstLetterStrict.txt -n {1}/no_definition_pairs_{2}_{3}.txt  "
                                  "-o {1}/word_pairs_{2}_{3}.txt -p all --l1 {4} --l2 {5} -l ".format(BASELINES_PATH, OUTPUT_PATH, lang1, lang2, acc1, acc2 ))
            # -l uses language dictionaies for negative examples, rather than only creating negative examples from the input file
            handleCommand(trainCreateCommand)

                
def featurizeSubstringTrainingPairsInParallel():
    featurizeCommand = ("./runSubstringFeaturizerOnExamplePairs.py  --parallelize --training --outputPath {0} --inputPath {0} --featureDictPath {0} "
                        "".format(OUTPUT_PATH ))
    handleCommand(featurizeCommand)


def featurizeSubstringTrainingPairsSequential():
    for i, langTuple in enumerate(langTuples):
        lang1, acc1 = langTuple
        for j in range(i, len(langTuples)):
            otherTuple = langTuples[j]
            lang2, acc2 = otherTuple
            featurizeTrainCommand = ("./runSubstringFeaturizerOnExamplePairs.py --training -i {0}/no_definition_pairs_{1}_{2}.txt -f {0}/feature_dict_{1}_{2}.txt "
                                     " -o {0}/substring_feature_values_{1}_{2}.txt".format(OUTPUT_PATH, lang1, lang2))
            handleCommand(featurizeTrainCommand)


def learnSubstringModels():
    # learn the svm models for each features file
    for i, langTuple in enumerate(langTuples):
        lang1, acc1 = langTuple
        for j in range(i, len(langTuples)):
            otherTuple = langTuples[j]
            lang2, acc2 = otherTuple
            learnModelCommand = "./svm_learn {0}/substring_feature_values_{1}_{2}.txt {0}/substring_model_{1}_{2}.txt".format(OUTPUT_PATH, lang1, lang2)
            handleCommand(learnModelCommand)
            

import optparse

parser = optparse.OptionParser()

parser.add_option('-p', action='store_true', dest='parallel', help="use flag if want to featurize in parallel.", default=False)
parser.add_option('-d', action='store_true', dest='debug', help="use flag if want to just print the commands that woudl be executed.", default=False)
options, args = parser.parse_args()

if options.debug:
    handleCommand = handleCommand.handleCommandJustPrint
else:
    handleCommand = handleCommand.handleCommandPrintAndExecute


createSubstringTrainingPairs()
if options.parallel:
    featurizeSubstringTrainingPairsInParallel()
else:
    featurizeSubstringTrainingPairsSequential()

learnSubstringModels()

