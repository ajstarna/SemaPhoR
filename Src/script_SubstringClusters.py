#!/usr/bin/env python3

# this script runs the necessary files to create the output clusters from the substring classified Algonquian pairs.
# these final clusters come from a combination of the general and specific model scores.
# use the -e argument to evaluate the clusters afterwards


import handleCommand

GENERAL_FEATURES_PATH = "../Output/GeneralFeatures"
SUBSTRING_FEATURES_PATH = "../Output/SubstringFeatures"
CLUSTERS_PATH = "../Output/SubstringClusters"



def clusterWithSubstringScores():
    clusterCommand = ("./clusterByScores.py -p {0}/positive_classified_pairs_all_langs.txt -l --sp {1}/substring_positive_classified_pairs_all_langs.txt "
                      "--progress -t 0 -c {2}/clusters_0.35Threshold_WithSubstring.txt --noSameLang".format(GENERAL_FEATURES_PATH, SUBSTRING_FEATURES_PATH, CLUSTERS_PATH))
    handleCommand(clusterCommand)


def evaluateSubstringClusters():
    evaluateCommand = ("./CognateClustersEvaluator.py -d -i {0}/clusters_0.35Threshold_WithSubstring.txt".format(CLUSTERS_PATH))
    handleCommand(evaluateCommand)
    totalRecallCommand = "./annotateOutput.py -e -i {0}/clusters_0.35Threshold_WithSubstring.txt".format(CLUSTERS_PATH)
    handleCommand(totalRecallCommand)


import optparse

parser = optparse.OptionParser()

parser.add_option('-e', action='store_true', dest='evaluate', help="use flag if want to evaluate the clusters already produced by this script")
parser.add_option('-d', action='store_true', dest='debug', help="use flag if want to just print the commands that woudl be executed.", default=False)
options, args = parser.parse_args()

if options.debug:
    handleCommand = handleCommand.handleCommandJustPrint
else:
    handleCommand = handleCommand.handleCommandPrintAndExecute



if options.evaluate:
    evaluateSubstringClusters()
else:
    clusterWithSubstringScores()

