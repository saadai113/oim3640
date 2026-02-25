n=5
while n!=0:
    print(n)
    n-=2

print('after while loop, n is', n)

def uses_any(word, letters):
    """Return True if any letter in 'letters' is in 'word'."""
    for letter in letters:
        if letter in word:
            return True
        else:
            return False

print(uses_any("hello", "aeiou"))  # True
print(uses_any("hello", "xyz"))    # False

import random
def random_letter():
    """Return a random letter from the alphabet."""
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    return random.choice(alphabet)
print(random_letter())

name="chloe"
name[1:3]