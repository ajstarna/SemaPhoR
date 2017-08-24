#!/usr/bin/env python3

# this script runs the necessary files to create and evaluate the baselines

BASELINES_PATH = "../Output/Baselines"

import handleCommand

def createBaselines():
    # used to create the baseline files. 4 different configurations. Strict versus non strict defs and with/without first letter matching criteria
    nonStrictCommand = "./findIdenticalDefs.py -s {0}/NonStrict.txt -d ".format(BASELINES_PATH)
    handleCommand(nonStrictCommand)

    strictCommand = "./findIdenticalDefs.py -s {0}/Strict.txt -d -t ".format(BASELINES_PATH)
    handleCommand(strictCommand)

    firstLetterNonStrictCommand = "./findIdenticalDefs.py -s {0}/FirstLetterNonStrict.txt -d -f ".format(BASELINES_PATH)
    handleCommand(firstLetterNonStrictCommand)

    firstLetterStrictCommand = "./findIdenticalDefs.py -s {0}/FirstLetterStrict.txt -d -t -f ".format(BASELINES_PATH)
    handleCommand(firstLetterStrictCommand)


def evaluateSystemOutput():
    # this will evaulate the various metrics script on the different baselines
    
    evaluateMaxRecallCommand = "./CognateClustersEvaluator.py --maxRecall"
    evaluateMaxPrecisionCommand = "./CognateClustersEvaluator.py --maxPrecision"
    handleCommand(evaluateMaxRecallCommand)
    handleCommand(evaluateMaxPrecisionCommand)

    baselines = ["{0}/Strict.txt".format(BASELINES_PATH),
                 "{0}/NonStrict.txt".format(BASELINES_PATH),
                 "{0}/FirstLetterStrict.txt".format(BASELINES_PATH),
                 "{0}/FirstLetterNonStrict.txt".format(BASELINES_PATH)]


    for baseline in baselines:
        evaluateCommand = "./CognateClustersEvaluator.py -d  -i {0} ".format(baseline)
        totalRecallCommand = "./annotateOutput.py -i {0} -e".format(baseline)
        handleCommand(evaluateCommand)
        handleCommand(totalRecallCommand)

import optparse

parser = optparse.OptionParser()

parser.add_option('-d', action='store_true', dest='debug', help="use flag if want to just print the commands that woudl be executed.", default=False)
options, args = parser.parse_args()

if options.debug:
    handleCommand = handleCommand.handleCommandJustPrint
else:
    handleCommand = handleCommand.handleCommandPrintAndExecute



createBaselines()
evaluateSystemOutput()
