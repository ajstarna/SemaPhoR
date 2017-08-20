#!/usr/bin/env python3

# this script runs the necessary files to create the alignment values between each Algonquian language pair


import handleCommand

ALIGNMENT_VALUES_OUTPUT_PATH = "../Output/AlignmentValues"

import optparse

parser = optparse.OptionParser()

parser.add_option('-d', action='store_true', dest='debug', help="use flag if want to just print the commands that woudl be executed.", default=False)
options, args = parser.parse_args()

if options.debug:
    handleCommand = handleCommand.handleCommandJustPrint
else:
    handleCommand = handleCommand.handleCommandPrintAndExecute



langTuples = [("cree", "C"), ("fox", "F"), ("meno", "M"), ("oji", "O")]
for i, langTuple in enumerate(langTuples):
    lang1, acc1 = langTuple
    for j in range(i, len(langTuples)):
        otherTuple = langTuples[j]
        lang2, acc2 = otherTuple
        
        prepareCommand = ("./createPreparedALINEFileForLangDicts.py --l1 {0} --l2 {1}"
                          " -o {4}/preparedALINEFile{2}{3}.txt".format(acc1, acc2, lang1, lang2, ALIGNMENT_VALUES_OUTPUT_PATH))
        handleCommand(prepareCommand)
        

        nusimilCommand = "time cat {0}/preparedALINEFile{1}{2}.txt | ./nusimil > {0}/nusimilOutput{1}{2}.txt".format(ALIGNMENT_VALUES_OUTPUT_PATH, lang1, lang2)
        handleCommand(nusimilCommand)
        
        # get rid of first 2 lines since they are not needed                                                                                                                                        
        removeLinesCommand = "time sed -i -e '1,2d' {0}/nusimilOutput{1}{2}.txt".format(ALIGNMENT_VALUES_OUTPUT_PATH, lang1, lang2)
        handleCommand(removeLinesCommand)


        writeBinaryCommand = ("./createAlignmentFeaturesFromNusimilOutput.py -n {0}/nusimilOutput{1}{2}.txt "
                              "-p {0}/preparedALINEFile{1}{2}.txt -o {0}/alignment_features_{1}_{2}_0.35Threshold.bin -t 0.35".format(ALIGNMENT_VALUES_OUTPUT_PATH, lang1, lang2))
        handleCommand(writeBinaryCommand)

        # once the alignFeature binary files are created, delete the preparedALINE and nusimilOutput files, since they are large and only intermediate steps                                        
        removeCommand = "rm {0}/prepared* {0}/nusimil*".format(ALIGNMENT_VALUES_OUTPUT_PATH)
        handleCommand(removeCommand)

