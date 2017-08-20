#!/usr/bin/env python3
''' this module is used to read and parse language dictionary XML files. 

the files look like this:

<?xml version="1.0" encoding="UTF-8"?>
<lexicon lang="cree" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="lexicon.xsd">
<entry><form>aːčikeːhweːw</form><pos>v</pos><sense><def><en>he trips him</en></def></sense></entry>
<entry><form>aːčikeːweːpahweːw</form><pos>v</pos><sense><def><en>he trips and throws him</en></def></sense></entry>
<entry><form>aːčimeːw</form><pos>v</pos><sense><def><en>he tells of him</en></def></sense></entry>
<entry><form>aːčimikosiw</form><pos>v</pos><sense><def><en>he is talked about</en></def></sense></entry>
<entry><form>aːčimoːw</form><pos>v</pos><sense><def><en>he tells his (own) story, he narrates</en></def></sense></entry>
<entry><form>aːčimoːwin</form><pos>n</pos><sense><def><en>story</en></def></sense></entry>
...
...
...
</lexicon>

'''

from collections import defaultdict
import xml.etree.ElementTree as ET


DATA_PATH = "../Data"
class LanguageDictParser(object):

    def __init__(self, langs, files, definitionLanguage):
        ''' init takes a list of langs (capital letters) and a list of filenames. 
            It is required that they are in the same order, i.e. the lang corresponds to the filename at the same index in the lists. '''
        self.langs = langs
        self.files = files
        self.definitionLanguage = definitionLanguage
        self.parseAllFiles()


    def parseAllFiles(self):
        ''' main method to parse all files that were given to the constructor and returns a dictionary of dictionaries, 
            mapping language letters to dictionaries which map words (in unicode) to definitions. '''

        self.result = dict() # dict mapping to dictionaries for each languge e.g "C" -> maps to dictionary of cree words to lists of definitions

        index = 0
        while index < len(self.langs):
            currentLang = self.langs[index]
            currentFileName = self.files[index]
            self.readFile(currentLang, currentFileName)
            index += 1
        return self.result




    def readFile(self, currentLang, currentFileName, dataPath=DATA_PATH):
        ''' method for reading and parsing a given fileName. Adds the information to self.result '''

        e = ET.parse(dataPath + "/" +  currentFileName).getroot() # if the directory of the language xml files changes, then this needs to be changed

        thisLangDict = defaultdict(list)

        for entry in e.findall("entry"):
            form = entry.find("form")
            try:
                word = form.text
            except:
                print("problem with entry: {0}".format(entry))
                exit(-1)
            if " " in word:
                # if contains a space then probably two words so ignore it
                continue


            loan = form.get('LOAN')
            if not loan is None:
                #print("Loan is {0}\n".format(loan))
                if loan == "spa":
                    # if word is a spanish loan, then ignore it
                    continue
                else:
                    print("Other type of loan")

            sense = entry.find("sense")
            if sense is None:
                continue
            for defn in sense.findall("def"):
                try:
                    defnText = defn.find(self.definitionLanguage).text
                except:
                    print("none type for def lang for word: {0}".format(word))
                    #exit(-1)
                    continue
                if defnText is None:
                    continue
                else:
                    # some of the language dicts have the same word with the exact same definition, 
                    # so check for this and don't add a duplicate
                    if not defnText in thisLangDict[word]:
                        thisLangDict[word].append(defnText)

        self.result[currentLang] = thisLangDict



    def printAllFiles(self):
        for lang in self.langs:
            for word in sorted(self.result[lang]):
                print(word)
                for defn in self.result[lang][word]:
                    print(defn)
                print()


    def __iter__(self):
        return iter(self.result.values())


    def getLangs(self):
        return self.langs

    def __getitem__(self, acc):
        return self.result[acc]



class AlgonquianLanguageDictParser(LanguageDictParser):
    langs = ["C", "F", "M", "O"]
    files = ["cree.xml", "fox.xml", "meno.xml", "oji.xml"]
    definitionLanguage = "en"

    def __init__(self):
        self.parseAllFiles()
