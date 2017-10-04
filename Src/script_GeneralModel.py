#!/usr/bin/env python3

# this script runs the necessary files to train the general model


import handleCommand

OUTPUT_PATH = "../Output/GeneralModel"


import optparse

parser = optparse.OptionParser()

parser.add_option('-d', action='store_true', dest='debug', help="use flag if want to just print the commands that woudl be executed.", default=False)
options, args = parser.parse_args()

if options.debug:
    handleCommand = handleCommand.handleCommandJustPrint
else:
    handleCommand = handleCommand.handleCommandPrintAndExecute




trainingPairsCommand = ("./createExamplePairsFromInputSets.py -p 5000 -n 10  -i ../Data/GoldSetsPolynesian.txt -s "
                        "-o {0}/training_pairs_polynesian.txt".format(OUTPUT_PATH))
handleCommand(trainingPairsCommand)



prepareCommand = ("./createPreparedALINEFileForExamples.py -i {0}/training_pairs_polynesian.txt "
                  "-o {0}/preparedALINEFile_training_pairs_polynesian.txt".format(OUTPUT_PATH))
handleCommand(prepareCommand)
nusimilCommand = "time cat {0}/preparedALINEFile_training_pairs_polynesian.txt | ./nusimil > {0}/nusimilOutput_training_pairs_polynesian.txt".format(OUTPUT_PATH)
handleCommand(nusimilCommand)
removeLinesCommand = "time sed -i -e '1,2d' {0}/nusimilOutput_training_pairs_polynesian.txt".format(OUTPUT_PATH) # get rid of first 2 lines since they are not needed
handleCommand(removeLinesCommand)
writeBinaryCommand = ("./createAlignmentFeaturesFromNusimilOutput.py -n {0}/nusimilOutput_training_pairs_polynesian.txt " 
                      "-p {0}/preparedALINEFile_training_pairs_polynesian.txt -o {0}/alignment_features_training_pairs_polynesian.bin".format(OUTPUT_PATH))
handleCommand(writeBinaryCommand)
removeCommand = "rm {0}/prepared* {0}/nusimil*".format(OUTPUT_PATH)
handleCommand(removeCommand)



featurizeTrainCommand = ("./runGeneralFeaturizerOnExamplePairs.py -i {0}/training_pairs_polynesian.txt -f {0}/feature_values_polynesian.txt "
                         " -a {0}/alignment_features_training_pairs_polynesian.bin  -y wordNet".format(OUTPUT_PATH))

handleCommand(featurizeTrainCommand)

learnCommand = "svm_learn {0}/feature_values_polynesian.txt {0}/polynesian_model.txt".format(OUTPUT_PATH)
handleCommand(learnCommand)


