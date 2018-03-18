import sys
import os
import glob

bcovCum = {}
lcovCum = {}
fcovCum = {}

prefix = sys.argv[1]
nexp = int(sys.argv[2])

outf = open(prefix + ".data", 'w')
outf.write ("# 1 n 2 bcov 3 lcov 4 fcov 5 t 6 fail 7 cbcov 8 clcov 9 cfcov 10 ct 11 cfail\n")

tCum = 0
failCum = 0

for n in xrange(0,nexp+1):
    dir = prefix + "." + str(n)
    bc = 0
    for b in open(dir + "/t.bcov"):
        bc += 1
        if b not in bcovCum:
            bcovCum[b] = True
    lc = 0
    for l in open(dir + "/t.lcov"):
        lc += 1
        if l not in lcovCum:
            lcovCum[l] = True
    fc = 0
    for f in open(dir + "/t.fcov"):
        fc += 1
        if f not in fcovCum:
            fcovCum[f] = True
    tc = len(glob.glob(dir + "/t.tc*.test.gz"))
    tc += len(glob.glob(dir + "/t.tc*.test"))
    failc = len(glob.glob(dir + "/t.tc*.out.gz"))
    failc += len(glob.glob(dir + "/t.tc*.out"))

    tCum += tc
    failCum += failc
    
    outf.write(str(n) + " " + str(bc) + " " + str(lc) + " " + str(fc) + " ")
    outf.write(str(tc) + " " + str(failc) + " ")
    outf.write(str(len(bcovCum)) + " ")
    outf.write(str(len(lcovCum)) + " ")
    outf.write(str(len(fcovCum)) + " ")
    outf.write(str(tCum) + " " + str(failCum) + "\n")

outf.close()
