import sys

ver = sys.argv[1]

outf = open(ver + ".merge.data",'w')

outf.write("bcov lcov fcov t fail cbcov clcov cfcov ct cfail swarm\n")
n = 0
for l in open(ver + ".swarm.data"):
    d = l.split()
    if d[0] != "#":
        outf.write(str(n))
        for v in d[1:]:
            outf.write(" ")
            outf.write(v)
        outf.write(" 1\n")
        n += 1
for l in open(ver + ".noswarm.data"):
    d = l.split()
    if d[0] != "#":
        outf.write(str(n))
        for v in d[1:]:
            outf.write(" ")
            outf.write(v)
        outf.write(" 0\n")
        n += 1
outf.close()
