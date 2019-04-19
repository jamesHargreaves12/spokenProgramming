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


def print_parallel(list1,list2):
    output1 = ""
    output2 = ""
    for x,y in zip(list1,list2):
        length = max(len(x),len(y))
        output1 += " " + x
        output2 += " " + y
        for i in range(length-len(x)):
            output1 += "-"
        for i in range(length-len(y)):
            output2 += "-"
    print(output1)
    print(output2)


def print_edit_dist_align(source, target, penalty_functions=levenshtein_distance):
    source.insert(0, "-")
    target.insert(0, "-")

    # Initialisation
    n = len(source)
    m = len(target)
    del_cost, ins_cost, sub_cost = penalty_functions
    F = [[0 for _ in target] for _ in source]
    P = [[0 for _ in target] for _ in source]
    for i in range(1, n):
        F[i][0] = F[i - 1][0] + ins_cost(source[i])
        P[i][0] = 1
    for j in range(1, m):
        F[0][j] = F[0][j - 1] + del_cost(target[j])
        P[0][j] = 2

    #   Main iteration
    for i, j in product(range(1, n), range(1, m)):
        F[i][j] = min(F[i - 1][j] + ins_cost(source[i]),
                      min(F[i][j - 1] + del_cost(target[j]), F[i - 1][j - 1] + sub_cost(source[i], target[j])))
        if F[i][j] == F[i - 1][j] + ins_cost(source[i]):
            P[i][j] = 1
        elif F[i][j] == F[i][j - 1] + del_cost(target[j]):
            P[i][j] = 2
        else:
            P[i][j] = 3
    # Termination

    if F[n-1][m-1] == 0:
        return

    source_out = []
    target_out = []
    i,j = n-1,m-1
    while i+j != 0:
        if P[i][j] == 1:
            source_out.insert(0,source[i])
            target_out.insert(0,"-")
            i=i-1
        if P[i][j] == 2:
            source_out.insert(0,"-")
            target_out.insert(0,target[j])
            j=j-1
        if P[i][j] == 3:
            source_out.insert(0,source[i])
            target_out.insert(0,target[j])
            i=i-1
            j=j-1
    print_parallel(source_out,target_out)



def minimum_edit_distance_per_token(source,target):
    return minimum_edit_distance(source,target)/len(target)


if __name__ == "__main__":
    modified_levenshtein_distance = (lambda x:1,lambda y:1,lambda x,y: 0 if x == y else 1)
    print(minimum_edit_distance([x for x in "execution"],[y for y in "intention"],modified_levenshtein_distance))

    transcript = "VARIABLE * NUMBER * NUMBER".split()
    pseudocode = "VARIABLE * NUMBER * NUMBER".split()
    print(minimum_edit_distance(transcript,pseudocode))

    transcript = "EMPTY_LIST VARIABLE for VARIABLE in VARIABLE if VARIABLE > FUNCTION_CALL VARIABLE VARIABLE for VARIABLE return VARIABLE".split()
    pseudocode = "VARIABLE = EMPTY_LIST for VARIABLE in VARIABLE if VARIABLE > VARIABLE FUNCTION_CALL VARIABLE VARIABLE return VARIABLE".split()
    print_edit_dist_align(transcript, pseudocode)
    print(minimum_edit_distance(transcript,pseudocode))

    transcript_convert = "VARIABLE return VARIABLE VARIABLE = VARIABLE * NUMBER * NUMBER".split(" ")
    pseudocode = "VARIABLE = VARIABLE * NUMBER VARIABLE = VARIABLE * NUMBER return VARIABLE".split(" ")
    print(minimum_edit_distance(transcript_convert,pseudocode))