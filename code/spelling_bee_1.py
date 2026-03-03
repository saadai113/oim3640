fin = open('../data/words.txt')
word_list = fin.read().split()
word_set = set(word_list)  # O(1) lookup instead of O(n)

def is_valid(word_set):
    if len(word_set) > 1 and list(word_set)[0] != list(word_set)[1]:
        return True
    return False

        


def spelling_bee(word, available, required):
    """Check whether a word is acceptable.
    
    >>> check_word('color', 'ACDLORT', 'R')
    True
    >>> check_word('ratatat', 'ACDLORT', 'R')
    True
    >>> check_word('rat', 'ACDLORT', 'R')
    False
    >>> check_word('told', 'ACDLORT', 'R')
    False
    >>> check_word('bee', 'ACDLORT', 'R')
    False
    """
    """the above is only an example...use the instructions outlined in the prompt"""
    if len(word) < 4:
        return False
    if required.lower() not in word.lower():
        return False
    for letters in word.lower():
        if letters not in available.lower():
             return False
    return True

print(spelling_bee('roar', 'aofrtpl', 'r'))        # True
print(spelling_bee('available', 'aofrtpl', 'r'))   # False