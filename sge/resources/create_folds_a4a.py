import random

LINES = 25398
COLUMNS = 59

f = open("resources/Audiology/a4a_folds.txt","w")
for i in range(100):
    ll = random.sample(range(0, LINES - 1), 7619)
    ll.sort()
    for value in ll:
        f.write(str(value) + " ")
    f.write('\n')
 