#!/usr/bin/env python3

# this script runs the necessary files to create the substring features for each Algonquian language pair and then
# classifies each pair using the specific substring models that were trained on each language pair
# use the -p argument for parallelizing. Otherwise, it is run sequential and takes longer.


import handleCommand

GENERAL_FEATURES_PATH = "../Output/GeneralFeatures"
SUBSTRING_FEATURES_PATH = "../Output/SubstringFeatures"
MODEL_PATH = "../Output/SubstringModels"

langTuples = [("cree", "C"), ("fox", "F"), ("meno", "M"), ("oji", "O")]



def createSubstringTestingPairs():
    # creates testing the positive classified pairs from the general SVM. 
    # the output files are the "full info" pairs file and the example pairs file (for featurizing)
    for i, langTuple in enumerate(langTuples):
        lang1, acc1 = langTuple
        for j in range(i, len(langTuples)):
            otherTuple = langTuples[j]
            lang2, acc2 = otherTuple
            if lang1 == lang2:
                sameLang = "-s"
            else:
                sameLang = ""
            createCommand = ("./createExamplePairsFromClassifiedPairs.py -c {0}/positive_classified_pairs_{2}_{3}.txt " 
                             " -o {1}/word_pairs_{2}_{3}.txt -n {1}/no_definition_pairs_{2}_{3}.txt {4}".format(GENERAL_FEATURES_PATH, SUBSTRING_FEATURES_PATH, lang1, lang2, sameLang ))
            handleCommand(createCommand)


def featurizeSubstringTestingPairsInParallel():
    featurizeCommand = ("./runSubstringFeaturizerOnExamplePairs.py  --parallelize --testing --outputPath {0} --inputPath {0} --featureDictPath {1} "
                        "".format(SUBSTRING_FEATURES_PATH, MODEL_PATH ))
    handleCommand(featurizeCommand)



def featurizeSubstringTestingPairsSequential():
    for i, langTuple in enumerate(langTuples):
        lang1, acc1 = langTuple
        for j in range(i, len(langTuples)):
            otherTuple = langTuples[j]
            lang2, acc2 = otherTuple
            featurizeTrainCommand = ("./runSubstringFeaturizerOnExamplePairs.py --testing -i {0}/no_definition_pairs_{2}_{3}.txt -f {1}/feature_dict_{2}_{3}.txt "
                                     " -o {0}/substring_feature_values_{2}_{3}.txt".format(SUBSTRING_FEATURES_PATH, MODEL_PATH, lang1, lang2))
            handleCommand(featurizeTrainCommand)
        


def classifySubstringTestingPairs():
    # we have the features, so now can used the learned model to classify these features
    for i, langTuple in enumerate(langTuples):
        lang1, acc1 = langTuple
        for j in range(i, len(langTuples)):
            otherTuple = langTuples[j]
            lang2, acc2 = otherTuple

            classifyCommand = ("./svm_classify {0}/substring_feature_values_{2}_{3}.txt {1}/substring_model_{2}_{3}.txt "
                               "{0}/substring_predictions_{2}_{3}.txt".format(SUBSTRING_FEATURES_PATH, MODEL_PATH, lang1, lang2))
            handleCommand(classifyCommand)



def formatOutputSubstringTestingPairs():
    # takes the prediction scores, the full info pairs, and the features file, and combines them together in a readable form of classified pairs
    # these output files have the svm score, features, and word pair all together
    for i, langTuple in enumerate(langTuples):
        lang1, acc1 = langTuple
        for j in range(i, len(langTuples)):
            otherTuple = langTuples[j]
            lang2, acc2 = otherTuple
            formatCommand = ("./formatSvmOutput.py -s {0}/substring_predictions_{1}_{2}.txt -p {0}/word_pairs_{1}_{2}.txt -f {0}/substring_feature_values_{1}_{2}.txt "  
                             " > {0}/substring_positive_classified_pairs_{1}_{2}.txt".format(SUBSTRING_FEATURES_PATH, lang1, lang2))
            handleCommand(formatCommand)


def combineClassifiedSubstringTestingPairs():
    combineFilesCommand = ("cat {0}/substring_positive_classified_pairs_*.txt "  
                           " > {0}/substring_positive_classified_pairs_all_langs.txt".format(SUBSTRING_FEATURES_PATH))
    handleCommand(combineFilesCommand)


import optparse

parser = optparse.OptionParser()

parser.add_option('-p', action='store_true', dest='parallel', help="use flag if want to featurize in parallel.", default=False)
parser.add_option('-d', action='store_true', dest='debug', help="use flag if want to just print the commands that woudl be executed.", default=False)
options, args = parser.parse_args()

if options.debug:
    handleCommand = handleCommand.handleCommandJustPrint
else:
    handleCommand = handleCommand.handleCommandPrintAndExecute

createSubstringTestingPairs()
if options.parallel:
    featurizeSubstringTestingPairsInParallel()
else:
    featurizeSubstringTestingPairsSequential()

classifySubstringTestingPairs()
formatOutputSubstringTestingPairs()
combineClassifiedSubstringTestingPairs()
