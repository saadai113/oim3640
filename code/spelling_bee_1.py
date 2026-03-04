import os

words_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../data/words.txt')
fin = open(words_path)
word_list = fin.read().split()
word_set = set(word_list)  # O(1) lookup instead of O(n)

def is_valid(word):
    return word in word_set


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

def find_pangrams(available, required):
    results = []
    for word in word_list:
        if spelling_bee(word, available, required):
            if all(letter in word.lower() for letter in available.lower()):
                results.append(word)
    return results

print(spelling_bee('roar', 'aofrtpl', 'r'))        # True
print(spelling_bee('available', 'aofrtpl', 'r'))   # False
print(find_pangrams('aofrtpl', 'r'))               # List of pangram words
print(spelling_bee('flattop', 'aofrtpl', 'r'))     # True
print(find_pangrams('flattop', 't'))               # List of pangram words