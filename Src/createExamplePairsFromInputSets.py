#!/usr/bin/env python3

from ExampleCreator import TwoLanguagesFromSetsExampleCreator, \
    AllLangsFromSetsExampleCreator, SimilarityInfoAllLangsFromSetsExampleCreator

import optparse
import sys

parser = optparse.OptionParser()
parser.add_option('-i', action='store', dest='inputFileName', help="the input name for the gold sets (or def sets) file")

parser.add_option('-o', action='store', dest='outputFileName', help="the output name for the example pairs with definitions.")
parser.add_option('-n', action='store', dest='noDefinitionsOutputFileName', help="the output name for the example pairs without definitions (like how the substring featurizer expects).")


parser.add_option('--l1', action='store', dest='lang1', help="the language acc for the first language. e.g 'C', 'F', 'M', 'O'")
parser.add_option('--l2', action='store', dest='lang2', help="the language acc for the second language. e.g 'C', 'F', 'M', 'O'")
parser.add_option('--family', action='store', dest='family', help="language family. algonquian or totonac", default="algonquian")

parser.add_option('-l', action='store_true', dest='useLangDictsForNegatives', help="flag to use if want to use language dicts for negative examples.", default=False)
parser.add_option('-r', action='store', dest='negativeRatio', help="the number of negative examples to use compared to positive exampls. default = 10", default=10)
parser.add_option('-p', action='store', dest='desiredNumberOfPositives', 
                  help="the number of desired positive examples to create. default = 10000. Or input 'all' to create all positive pairs", default=10000)
parser.add_option('-s', action='store_true', dest='similarityInfo', help="flag if want to use similarity info when construcitng positive examples")


parser.add_option('--defSets', '-d', action='store_true', dest='defSets', help="the flag if creating examples from an input of def sets.", default=False)
parser.add_option('--cogSets', '-c', action='store_true', dest='cogSets', help="the flag if creating examples from an input of cog sets.", default=False)

parser.add_option('--randomSeed', action='store_true', dest='randomSeed', help="the flag if want to provide the random seed for generating random negative examples."
                  "this allows for the same examples file to be reproduced.", default=100)




options, args = parser.parse_args()


if options.inputFileName is None:
    sys.stderr.write("Must provide input file name!\n")
    parser.print_help()
    exit(-1)


if options.outputFileName is None and options.noDefinitionsOutputFileName is None:
    sys.stderr.write("Must provide at least one output file name!\n")
    parser.print_help()
    exit(-1)


if options.lang1 is None or options.lang2 is None:
    sys.stderr.write("Looking at all languages!\n")

    if options.similarityInfo:
        with AllLangsFromSetsExampleCreator(options.inputFileName, options.outputFileName, options.noDefinitionsOutputFileName, options.desiredNumberOfPositives, int(options.negativeRatio), 
                                            options.useLangDictsForNegatives, options.family, options.defSets, int(options.randomSeed)) as creator:
            creator.run()
    else:
        with SimilarityInfoAllLangsFromSetsExampleCreator(options.inputFileName, options.outputFileName, options.noDefinitionsOutputFileName, options.desiredNumberOfPositives, int(options.negativeRatio), 
                                            options.useLangDictsForNegatives, options.family, options.defSets, int(options.randomSeed)) as creator:
            creator.run()

else:
    sys.stderr.write("Looking at {0} and {1} pairs!\n".format(options.lang1, options.lang2))
    with TwoLanguagesFromSetsExampleCreator(options.inputFileName, options.outputFileName, options.noDefinitionsOutputFileName, options.desiredNumberOfPositives, int(options.negativeRatio), 
                                            options.useLangDictsForNegatives, options.family, options.lang1, options.lang2, options.defSets, int(options.randomSeed)) as creator:
        creator.run()
    

