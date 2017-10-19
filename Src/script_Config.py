#!/usr/bin/env python3

import handleCommand
import optparse
import shutil
import sys

parser = optparse.OptionParser()

parser.add_option('-d', action='store_true', dest='debug', help="use flag if want to just print the commands that woudl be executed.", default=False)
options, args = parser.parse_args()

if options.debug:
    handleCommand = handleCommand.handleCommandJustPrint
else:
    handleCommand = handleCommand.handleCommandPrintAndExecute

mkdirCommand = "mkdir ../Output/AlignmentValues"
handleCommand(mkdirCommand)
mkdirCommand = "mkdir ../Output/Baselines"
handleCommand(mkdirCommand)
mkdirCommand = "mkdir ../Output/Clusters"
handleCommand(mkdirCommand)
mkdirCommand = "mkdir ../Output/GeneralFeatures"
handleCommand(mkdirCommand)
mkdirCommand = "mkdir ../Output/GeneralModel"
handleCommand(mkdirCommand)
mkdirCommand = "mkdir ../Output/SubstringClusters"
handleCommand(mkdirCommand)
mkdirCommand = "mkdir ../Output/SubstringFeatures"
handleCommand(mkdirCommand)
mkdirCommand = "mkdir ../Output/SubstringModels"
handleCommand(mkdirCommand)

# check for svm_learn and svm_classify in $PATH
if not shutil.which("svm_learn"):
  sys.exit("ERROR: Could not find svm_learn")
if not shutil.which("svm_classify"):
  sys.exit("ERROR: Could not find svm_classify")
