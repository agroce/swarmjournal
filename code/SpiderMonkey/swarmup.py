import sys
import random

infn = sys.argv[1]
outfn = sys.argv[2]
confn = sys.argv[3]

if len(sys.argv) > 4:
    random.seed(int(sys.argv[4]))

outf = open(outfn,'w')
outcf = open(confn, 'w')

n = 0

for line in open(infn):
    l = line.split()
    if ((l != []) and ((l[0] == "function(dr)") or
                       (l[0] == "function(depth)")) and("}," in line)):
        n = n + 1
        if (random.randint(0,1) == 0):
            outf.write(line)
            outcf.write("--" + str(n) + " ")
    elif ((l != []) and (l[0] == "case")):
        n = n + 1
        if (random.randint(0,1) == 0):
            outf.write(line)
            outcf.write("--" + str(n) + " ")
    else:
        outf.write(line)
