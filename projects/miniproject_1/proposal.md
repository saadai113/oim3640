# Objective: Make a trivia game of 10 questions related to Python
 - The questions are either from the sample list from a JSON file
 - It tracks your score, gives feedback after each answer, and shows a full review at the end. 
 - Features used: Terminal codes, f-srings, sys.exit(1), try / except for error handling, isinstance() for type checking
 - enumerate(),dict.get(), Sets and the | Operator, str.upper() and .strip(), str.index(),
 - random.sample(), generator expression in sum(), sys.argv, if __name__ == '__main__'
 - Changes made: No need to type Enter after every question
 - 10 questions are shown everytime
 - The app decide between the built-in questions or the JSON file in lines 293-297
 - The rule: if the user passes a command-line argument, it's treated as a file path and loaded as JSON. No argument = built-in questions.
 - Change: App will get 10 questions from questions.json file + 2 questions from in-built sample
 - Idea: App gets questions fromm scraping off net
 - 


## Implementation details
