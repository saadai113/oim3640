# Learning Log - Session Online

## Objective

Classwork focused on loops, string behavior, and small helper functions in [code/classonline.py](../code/classonline.py).

## What I learned

- A `while` loop keeps running while its condition is true. In the example, `n` starts at `5`, decreases by `2` each time, and the loop stops when `n` reaches `0`.
- A function can search for a letter by checking membership with `in`.
- A string cannot be changed in place. Methods like `replace` create a new string instead of modifying the original.
- Slicing works on strings, so `name[1:3]` returns a substring.

## Code patterns from the session

- `uses_any(word, letters)` checks whether any letter from `letters` appears in `word`.
- `random_letter()` chooses a random lowercase letter from the alphabet with `random.choice`.
- The slice example shows how to extract a portion of a string without changing the original value.

## Debugging note

- The first version of `uses_any` returns too early because the `return False` is inside the loop. That means it stops after checking only the first letter instead of checking all of them.