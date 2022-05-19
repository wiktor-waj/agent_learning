import json

# Script to create Q-Value JSON file, initilazing with zeros

qval = {}
for x in list(range(-80, 510, 5)):
    for y in list(range(-300, 800, 5)):
        for v in range(-10, 9):
            qval[str(x) + "_" + str(y) + "_" + str(v)] = [0, 0]


fd = open("data/qvalues.json", "w")
json.dump(qval, fd)
fd.close()
