import random

with open("wordlist.txt") as f:
    content = f.readlines()
    pw = ""
    for i in range(3):
	pw += content[random.randint(0, len(content))].strip().capitalize()
    print pw
