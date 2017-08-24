#!/usr/bin/env python3

import handleCommand
import optparse

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

