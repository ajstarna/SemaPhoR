#!/usr/bin/env python3

# this script runs the necessary files to create and evaluate the baselines

import handleCommand

GENERAL_FEATURES_PATH = "../Output/GeneralFeatures"
CLUSTERS_PATH = "../Output/Clusters"



def cluster():
    clusterCommand = ("./clusterByScores.py -p {0}/positive_classified_pairs_all_langs.txt -l "
                      "--progress -t 0  -c {1}/clusters_0.35Threshold.txt --noSameLang ".format(GENERAL_FEATURES_PATH, CLUSTERS_PATH))
    handleCommand(clusterCommand)


def evaluateClusters():
    evaluateCommand = ("./CognateClustersEvaluator.py -d -i {0}/clusters_0.35Threshold.txt --purity".format(CLUSTERS_PATH))
    handleCommand(evaluateCommand)
    totalRecallCommand = "./annotateOutput.py -d -e -i {0}/clusters_0.35Threshold.txt ".format(CLUSTERS_PATH )
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
    evaluateClusters()
else:
    cluster()

