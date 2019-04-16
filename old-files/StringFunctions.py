
def reverse(word):
    result = ""
    for letter in word:
        result = letter + result
    return result

def countOccurances(character, word):
    count = 0
    for letter in word:
        if (letter == character):
            count = count + 1
    return count

