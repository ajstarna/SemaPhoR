#!/usr/bin/env python3

# this script runs the necessary files to create the features for each Algonquian language pair and then
# classifies each pair using the general model that was trained on Polynesian data
# use the -p argument for parallelizing. Otherwise, it is run sequential and takes longer.

import handleCommand

GENERAL_FEATURES_PATH = "../Output/GeneralFeatures"
ALIGNMENT_PATH = "../Output/AlignmentValues"
MODEL_PATH = "../Output/GeneralModel"



langTuples = [("cree", "C"), ("fox", "F"), ("meno", "M"), ("oji", "O")]


def featurizeInParallel():
    # -r means read from threshold
    featurizeCommand = ("./runGeneralFeaturizerOnLangDicts.py  --parallelize --outputPath {0} --alignmentPath {1} -t 0.35 -r -y wordNet"
                        "".format(GENERAL_FEATURES_PATH, ALIGNMENT_PATH ))
    handleCommand(featurizeCommand)


def featurizeSequential():
    for i, langTuple in enumerate(langTuples):
        lang1, acc1 = langTuple
        for j in range(i, len(langTuples)):
            otherTuple = langTuples[j]
            lang2, acc2 = otherTuple
            # -r means read from threshold
            featurizeCommand = ("./runGeneralFeaturizerOnLangDicts.py  -f {0}/{2}_{3}_feature_values.txt "
                                "-p {0}/{2}_{3}_output_pairs.txt -a {1}/alignment_features_{2}_{3}_0.35Threshold.bin -r  -t 0.35 -y wordNet"
                                " --l1 {4} --l2 {5} ".format(GENERAL_FEATURES_PATH, ALIGNMENT_PATH, lang1, lang2, acc1, acc2))
            handleCommand(featurizeCommand)

            
def classify():
    for i, langTuple in enumerate(langTuples):
        lang1, acc1 = langTuple
        for j in range(i, len(langTuples)):
            otherTuple = langTuples[j]
            lang2, acc2 = otherTuple
            # we score the features using the pollex trained model
            classifyCommand = ("svm_classify {0}/feature_values_{2}_{3}.txt {1}/polynesian_model.txt "
                               "{0}/predictions_{2}_{3}.txt".format(GENERAL_FEATURES_PATH, MODEL_PATH, lang1, lang2))
            handleCommand(classifyCommand)

            
def formatClassifiedPairs():
    for i, langTuple in enumerate(langTuples):
        lang1, acc1 = langTuple
        for j in range(i, len(langTuples)):
            otherTuple = langTuples[j]
            lang2, acc2 = otherTuple
            
            # next we format so we have the word pairs with their scores
            # just get the positive scores, since otherwise the amount of pairs gets so huge that we run out of  memory when clustering
            formatSVMCommand = ("./formatSvmOutput.py -s {0}/predictions_{1}_{2}.txt -p {0}/word_pairs_{1}_{2}.txt "
                                "-f {0}/feature_values_{1}_{2}.txt > {0}/positive_classified_pairs_{1}_{2}.txt".format(GENERAL_FEATURES_PATH, lang1, lang2))
            handleCommand(formatSVMCommand)


def organizeOutputs():
    combinePairsCommand = "cat {0}/positive_classified_pairs* > {0}/positive_classified_pairs_all_langs.txt".format(GENERAL_FEATURES_PATH)
    handleCommand(combinePairsCommand)



import optparse

parser = optparse.OptionParser()

parser.add_option('-p', action='store_true', dest='parallel', help="use flag if want to featurize in parallel.", default=False)
parser.add_option('-d', action='store_true', dest='debug', help="use flag if want to just print the commands that woudl be executed.", default=False)
options, args = parser.parse_args()

if options.debug:
    handleCommand = handleCommand.handleCommandJustPrint
else:
    handleCommand = handleCommand.handleCommandPrintAndExecute



if options.parallel:
    featurizeInParallel()
else:
   featurizeSequential()
classify()
formatClassifiedPairs()
organizeOutputs()
