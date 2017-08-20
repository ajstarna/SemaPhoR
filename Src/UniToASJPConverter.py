# -*- coding: utf-8 -*-

''' module to use for converting unicode to ASJP 
function to import: uniToASJP '''


# this mapping is taken from uni2asjp.pl
u2a = {} # dict mapping unicode to asjp

u2a['\u0020'] = " ";	# spaces are preserved
u2a['\u0021'] = "";	# ! exclamation mark - ignored
u2a['\u0027'] = "";	# incorrect ejective mark? ignored
u2a['\u0028'] = "";	# ( opening bracket - ignored
u2a['\u0029'] = "";	# ) closing bracket - ignored
u2a['\u002D'] = "";	# hyphens indicate bound forms 
u2a['\u002E'] = "";	# dots -> TO DO
u2a['\u002F'] = "";	# slash indicates alternative forms -> TO DO
u2a['\u003D'] = "";	# equal sign indicates a clitic boundary
u2a['\u003F'] = "";	# question mark may be prosody or questionable entry (!)
u2a['\u0063'] = "c";	# alveolar affricate (NOT IPA voiceless palatal plosive)
u2a['\u0079'] = "y";	# palatal approximant (IPA: j)
u2a['\u00A1'] = "";	# inverted exclamation mark - ignored
u2a['\u00BF'] = "";	# inverted question mark - ignored
u2a['\u00E1'] = "a";	# a with acute (stress mark ignored)


u2a['\u00E6'] = "E";	

u2a['\u00E9'] = "e";	# e with acute (stress mark ignored)
u2a['\u00ED'] = "i";	# i with acute (stress mark ignored)
u2a['\u00F3'] = "o";	# o with acute (stress mark ignored)
u2a['\u00FA'] = "u";	# u with acute (stress mark ignored)
u2a['\u010D'] = "C";	# voiceless palato-alveolar affricate (not IPA)
u2a['\u014B'] = "N";	# voiced velar nasal
u2a['\u0161'] = "S";	# voiceless postalveolar fricative (not IPA)
u2a['\u019B'] = "L";	# voiceless coronal lateral (af)fricat(iv)e (not IPA)
u2a['\u0254'] = "O";	# open-mid back rounded vowel (ASJP "o")
u2a['\u0259'] = "3";	# mid-central vowel (schwa)
u2a['\u025B'] = "E";	# open-mid front unrounded vowel
u2a['\u0274'] = "N";	# smallcaps N 3 times in Misantla (map to uvular nasal?)
u2a['\u0294'] = "7";	# voiceless glotal stop
u2a['\u0272'] = "5";	# voiced palatal nasal
u2a['\u027E'] = "r";	# voiced coronal tap (mostly native)
u2a['\u02D0'] = "";	# vowel length is ignored
u2a['\u026A'] = "I";	# near-close front unrounded vowel (ASJP "i")
u2a['\u026C'] = "1";	# voiceless coronal lateral fricative (ASJP "L")
u2a['\u0330'] = "*";	# nasality subscript (IPA: superscript) 
u2a['\u03C7'] = "X";	# voiceless uvular fricative
u2a['\u2019'] = "\"";	# ejective apostrophe?


u2a['\u003A'] = "";	# colon - vowel length is ignored
u2a['\u0064'] = "d";	# not in Totonac
u2a['\u0066'] = "f";	# not in Totonac
u2a['\u0071'] = "q";	# voiceless uvular stop
u2a['\u007A'] = "z";	# not in Totonac
u2a['\u028E'] = "L";	# I assume this is palatal lateral approximant
u2a['\u02B0'] = "";	# aspiration ignored for now?
u2a['\u0283'] = "S";	# voiceless postalveolar fricative
u2a['\u033A'] = "";	# the "apical" diacritic - ignored
u2a['\u0109'] = "Q";	# MB: voiceless retroflex affricate (not IPA, not ASJP)




def uniToASJP(uniWord):
    ''' loops through each char and sees if it is in u2a mapping from uni to ASJP and replaces the char if so '''
    result = ""
    for char in uniWord:
        if char in u2a:
            result += u2a[char]
        else:
            result += char

    return result


if __name__ == "__main__":
    word = 'čeːqtanænehtakwat'
    print("uniWord = {0}".format(word))
    converted = uniToASJP(word)
    print("converted word = {0}".format(converted))





