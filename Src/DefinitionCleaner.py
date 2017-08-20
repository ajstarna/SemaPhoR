''' functions for handling, cleaning, splitting the definitions from the language xml files '''

import re 


def cleanDef(defn):
    ''' method to clean a definition and return the possibly multiple clean definitions as a single string, joined by semi colons.                                                                     
    this is the format used by the Featurizer '''
    splitClean = definitionCleanAndSplit(defn)
    return ";".join(splitClean)


def definitionCleanAndSplit(defn):
    defn = re.sub('\(.*?\)', '', defn)
    defs =  defn.replace(",", ";").split(";") # replace commas with semi colons and then split on semi colons. This is like splitting on commas and semicolons
    newDefs = cleanMultipleDefs(defs)
    return newDefs


def cleanMultipleDefs(defs):
    newDefs = []
    for defn in defs:
        newDef = cleanSingleDef(defn)
        if newDef == "":
            # don't want empty defintions
            continue
        newDefs.append(newDef)
    return newDefs


def cleanSingleDef(defn):
    newDef = re.sub('\(.*?\)', '', defn) # remove anythiing between parentheses (already happened on the full unsplit definition too
    newDef = re.sub(r'[/\\-]', ' ', newDef) # replace slashes with spaces in case words separated with slashes 
    newDef = re.sub('[.,\(\);\?\!\'\"\-¿<>]', '', newDef) # remove punctuation
    newDef = compactWhitespace(newDef)
    return newDef


def compactWhitespace(defn):
    defn = re.sub('^\s+', '', defn) # remove white space at the start
    defn = re.sub('\s+$', '', defn) # remove white space at the end
    defn = re.sub('\s+', ' ', defn) # replace multiple white space with one space
    return defn
