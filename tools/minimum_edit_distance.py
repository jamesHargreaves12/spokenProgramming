from itertools import product

# will be using the Needleman-wunsch algorithm see bioinformatics notes for details:
# Levenshtein distance = inserts and deletions have penalty 1, no substitutions (so is both insert and delete)
# penalty functions of the form (del-cost(source),ins-cost(target),sub_cost(source,target))
levenshtein_distance = (lambda x:1,lambda y:1,lambda x,y: 0 if x == y else 2)
def minimum_edit_distance(source,target,penalty_functions=levenshtein_distance):
    # note the algorithm assuming strings indexed from 1
    source.insert(0,"-")
    target.insert(0,"-")

    #Initialisation
    n = len(source)
    m = len(target)
    del_cost,ins_cost,sub_cost = penalty_functions
    F = [[0 for _ in target] for _ in source]
    for i in range(1,n):
        F[i][0] = F[i-1][0] + ins_cost(source[i])
    for j in range(1,m):
        F[0][j] = F[0][j-1] + del_cost(target[j])

    #   Main iteration
    for i,j in product(range(1,n),range(1,m)):
        F[i][j] = min(F[i-1][j] + ins_cost(source[i]),min(F[i][j-1] + del_cost(target[j]),F[i-1][j-1] + sub_cost(source[i],target[j])))

    # Termination
    source.pop(0)
    target.pop(0)
    return F[n-1][m-1]


if __name__ == "__main__":
    modified_levenshtein_distance = (lambda x:1,lambda y:1,lambda x,y: 0 if x == y else 1)
    print(minimum_edit_distance([x for x in "execution"],[y for y in "intention"],modified_levenshtein_distance))

    transcript = "VARIABLE * NUMBER * NUMBER".split()
    pseudocode = "VARIABLE * NUMBER * NUMBER".split()
    print(minimum_edit_distance(transcript,pseudocode))

    transcript = "EMPTY_LIST VARIABLE for VARIABLE in VARIABLE if VARIABLE > FUNCTION_CALL VARIABLE VARIABLE for VARIABLE return VARIABLE".split()
    pseudocode = "VARIABLE = EMPTY_LIST for VARIABLE in VARIABLE if VARIABLE > VARIABLE FUNCTION_CALL VARIABLE VARIABLE return VARIABLE".split()
    print(minimum_edit_distance(transcript,pseudocode))

    transcript_convert = "VARIABLE return VARIABLE VARIABLE = VARIABLE * NUMBER * NUMBER".split(" ")
    pseudocode = "VARIABLE = VARIABLE * NUMBER VARIABLE = VARIABLE * NUMBER return VARIABLE".split(" ")
    print(minimum_edit_distance(transcript_convert,pseudocode))