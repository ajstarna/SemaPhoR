#!/usr/bin/env python3

'''
This script reads in a classified pairs file and then creates the output pairs for the substring model to run on for each pair in the file.

'''

from ExampleCreator import ClassifiedPairExampleCreator 

import sys



if __name__ == "__main__":
    import optparse
    parser = optparse.OptionParser()
    parser.add_option('-c', action='store', dest='classifiedPairsFile', help="the input name for the classified pairs")


    parser.add_option('-o', action='store', dest='outputFileName', help="the output name for the example pairs with definitions.")
    parser.add_option('-n', action='store', dest='noDefinitionsOutputFileName', help="the output name for the example pairs without definitions (like how the substring featurizer expects).")

    parser.add_option('-s', action='store_true', dest='sameLang', help="flag if reading pairs from the same language.", default=False)

    options, args = parser.parse_args()


    if options.classifiedPairsFile is None:
        sys.stderr.write("Must provide file name!\n")
        parser.print_help()
        exit(-1)


    with ClassifiedPairExampleCreator(options.classifiedPairsFile, options.outputFileName, options.noDefinitionsOutputFileName, options.sameLang) as ec:
        ec.run()
