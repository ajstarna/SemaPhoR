# -*- coding: utf-8 -*-

''' module to use for converting ASJP to ALINE
function to import: asjpToASJP '''


a2a = {} # dict mapping ASJP to ALINE

a2a['\u0020'] = "";	# spaces are removed
a2a['\u0045'] = "aF";
a2a['\u004E'] = "gN";
a2a['\u0043'] = "cV";
a2a['\u0053'] = "sV";
a2a['\u004C'] = "cT";
a2a['\u004F'] = "oL";       # open-mid back rounded vowel
a2a['\u0033'] = "eC";       # mid-central vowel (schwa)
a2a['\u0037'] = "q";        # voiceless glotal stop
a2a['\u0035'] = "nP";       # voiced palatal nasal
a2a['\u0072'] = "r";        # voiced coronal tap (mostly native)
a2a['\u0049'] = "iL";       # near-close front unrounded vowel
a2a['\u0031'] = "sT";       # voiceless coronal lateral fricative
a2a['\u0058'] = "xU";       # voiceless uvular fricative
a2a['\u0051'] = "Q";        # voiceless uvular stop



def asjpToALINE(asjpWord):
    ''' loops through each char and sees if it is in a2a mapping from ASJP to ALINE and replaces the char if so '''
    result = ""
    for char in asjpWord:
        if char in a2a:
            result += a2a[char]
        else:
            result += char

    return result


if __name__ == "__main__":
    word = 'wiqSa3kwahSEkwi'
    print("uniWord = {0}".format(word))
    converted = asjpToALINE(word)
    print("converted word = {0}".format(converted))





