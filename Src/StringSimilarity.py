
''' file contains string similarity functions '''




def leven_with_alignment(s1, s2, substitutionCost=1):
    # the substitution cost is used to decide how to treat a mismatch. Some versions of levenshtein will only punish
    # a mismatch is given a default cost of 1
    length1 = len(s1)
    length2 = len(s2)

    D = []
    
    for i in range(length1 + 1):
        D.append([0]* (length2+1))
    # D is a length1xlength2 matrix
    for i in range(length1 + 1):
        D[i][0] = i
    for j in range(length2 + 1):
        D[0][j] = j


    for i in range(1, length1+1):
        for j in range(1, length2+1):
            left = D[i][j-1] + 1
            curr = D[i-1][j] + 1
            diag = D[i-1][j-1] + substitutionCost * (s1[i-1] != s2[j-1]) # here is where sub cost comes into play

            new = min(diag, curr, left)
            D[i][j] = new


    alignment = []
    i = length1
    j = length2
    while i > 0 or j > 0:
        try:
            if i > 0 and D[i][j] == (D[i-1][j] + 1): #  i > 0 check so we dont look above the matrix
                alignment.append((s1[i-1], "-"))
                #print("above")
                i -= 1
            elif j > 0 and D[i][j] == D[i][j-1] + 1: 
                # adding j > 0. don't think this is strictly necessary since if gets to this point then
                # we know either i is at 0 or that the above position isn't one lower than current score
                alignment.append(("-", s2[j-1]))
                j -= 1
            else:
                alignment.append((s1[i-1], s2[j-1]))
                i -= 1
                j -= 1
        except:
            for row in D:
                print(row)
            alignment.reverse()
            print(alignment)
            print("Problem with i = {0} and j = {1}, on word1 = {2}, word2 = {3}\n\n".format(i,j, s1, s2))
            exit(-1)
            break
        
    editDistance = D[-1][-1] # grab the editdistance from the D matrix
    alignment.reverse() # reverse the alignment so it goes from start to end of words
    return(editDistance, alignment) 




# function taken from https://en.wikibooks.org/wiki/Algorithm_Implementation/Strings/Levenshtein_distance on Oct 8, 2015
def levenshtein(s1, s2):
    if len(s1) < len(s2):
        return levenshtein(s2, s1)

    # len(s1) >= len(s2)
    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1 # j+1 instead of j since previous_row and current_row are one character longer
            deletions = current_row[j] + 1       # than s2
            substitutions = previous_row[j] + 2*(c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]


def NED(s1, s2):
    # normalized edit distance by the length of the longer word
    maxlen = max(len(s1), len(s2))
    ed = levenshtein(s1, s2)
    return float(ed) / maxlen


# function taken from http://rosettacode.org/wiki/Longest_common_subsequence on Oct.10, 2015
def lcs(a, b):
    lengths = [[0 for j in range(len(b)+1)] for i in range(len(a)+1)]
    # row 0 and column 0 are initialized to 0 already
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            if x == y:
                lengths[i+1][j+1] = lengths[i][j] + 1
            else:
                lengths[i+1][j+1] = \
                    max(lengths[i+1][j], lengths[i][j+1])
    # read the substring out from the matrix
    result = ""
    x, y = len(a), len(b)
    while x != 0 and y != 0:
        if lengths[x][y] == lengths[x-1][y]:
            x -= 1
        elif lengths[x][y] == lengths[x][y-1]:
            y -= 1
        else:
            assert a[x-1] == b[y-1]
            result = a[x-1] + result
            x -= 1
            y -= 1
    return result
