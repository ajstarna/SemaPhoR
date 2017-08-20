#!/usr/bin/env python3
''' module to use for converting unicode to ALINE and ALINE to unicode
functions to import: uniToALINE or alineToUni '''

# this mapping is taken from format_algo_cognates.pl 

u2a = {} # dict mapping unicode to ALINE

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


u2a['\u0020'] = "";	# spaces are removed
u2a['\u00E6'] = "aF";	# near-open front unrounded vowel (Algonquian)
u2a['\u010D'] = "cV";	# voiceless palato-alveolar affricate (not IPA)
u2a['\u014B'] = "gN";	# voiced velar nasal
u2a['\u0161'] = "sV";	# voiceless postalveolar fricative (not IPA)
u2a['\u019B'] = "cT";	#  voiceless coronal lateral (af)fricat(iv)e (not IPA)
u2a['\u0254'] = "oL";	# open-mid back rounded vowel
u2a['\u0259'] = "eC";	# mid-central vowel (schwa)
u2a['\u025B'] = "eL";	# open-mid front unrounded vowel
u2a['\u0274'] = "nU";	# smallcaps N 3 times in Misantla (map to uvular nasal?)
u2a['\u0294'] = "q";	# voiceless glotal stop
u2a['\u0272'] = "nP";	# voiced palatal nasal
u2a['\u027E'] = "r";	# voiced coronal tap (mostly native)
u2a['\u026A'] = "iL";	# near-close front unrounded vowel
u2a['\u026C'] = "sT";	# voiceless coronal lateral fricative
u2a['\u0330'] = "N";	# nasality subscript (IPA: superscript) 
u2a['\u03C7'] = "xU";	# voiceless uvular fricative
u2a['\u2019'] = "G";	# ejective apostrophe?

'''


based on perl code ali2uni.pl

my %M = ("c" => 0x0161, "j" => 0x010D, "3" => 0x00E6, "H" => 0x02D0 );

foreach ( qw / a e h i k m n o p q s t u w y / ) { $M{$_} = ord($_); }

while (<>) {
  chomp;
  printf "%s\n", encode('UTF-8', ali2uni($_));
}

sub ali2uni {
  my $word = $_[0];

  $word =~ s/aF/3/g;
  $word =~ s/cV/j/g;
  $word =~ s/sV/c/g;

  my @out = ();
  foreach my $l ( split(//, $word ) ) {
    if (defined($M{$l})) {
      push @out, chr($M{$l});
    } else {
      die unless $l =~ /[bgl]/;
    }
  }

  return join("", @out);
}

'''


a2u = {} # dict mapping ALINE to uni
a2u["c"] = '\u0161'
a2u["j"] = '\u010D'
a2u["3"] = '\u00E6'
a2u["H"] = '\u02D0'
a2u["a"] = 'a'
a2u["e"] = 'e'
a2u["h"] = 'h'
a2u["i"] = 'i'
a2u["k"] = 'k'
a2u["m"] = 'm'
a2u["n"] = 'n'
a2u["o"] = 'o'
a2u["p"] = 'p'
a2u["q"] = 'q'
a2u["s"] = 's'
a2u["t"] = 't'
a2u["u"] = 'u'
a2u["w"] = "w"
a2u["y"] = "y"


def uniToALINE(uniWord):
    ''' loops through each char and sees if it is in u2a mapping from uni to ALINE and replaces the char if so '''
    result = ""
    for char in uniWord:
        if char in u2a:
            result += u2a[char]
        else:
            result += char
    return result.replace("L", "") # Jan 20: the 'L' doesn't matter really, plus it messes up nusimil


def alineToUni(alineWord):
    result = ""
    alineWord = alineWord.replace("aF", "3").replace("cV", "j").replace("sV", "c")
    for char in alineWord:
        if char in a2u:
            result += a2u[char]
        elif char in ['b', 'g', 'l']:
            continue
        else:
            exit(-1)
    return result

if __name__ == "__main__":
    word = "aːhpaweːwa"
    word2 = "aːppaweː"
    print("uniWord = {0}".format(word))
    converted = uniToALINE(word)
    print("converted word = {0}".format(converted))
    print("uniWord = {0}".format(word2))
    converted = uniToALINE(word2)
    print("converted word = {0}".format(converted))





