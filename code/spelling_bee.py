fin = open('../data/words.txt')
word_list = fin.read().split()
word_set = set(word_list)  # O(1) lookup instead of O(n)


def is_valid(word):
    return word in word_set


def spelling_bee(word, available, required):
    if len(word) < 4:
        return False
    if required.lower() not in word.lower():
        return False
    for letter in word.lower():
        if letter not in available.lower():
            return False
    return True


def find_words(available, required):
    results = []
    for word in word_list:
        if is_valid(word) and spelling_bee(word, available, required):
            results.append(word)
    return results


# Replace these with today's NYT Spelling Bee letters
available = 'aofrtpl'   # all 7 letters
required  = 'r'         # center letter (must appear)

results = find_words(available, required)
print(f"Found {len(results)} words:")
for word in sorted(results):
    print(word)
