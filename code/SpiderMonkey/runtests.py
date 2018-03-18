import subprocess
import sys
import time
import os
import runTest
import coverage

prefix = sys.argv[1]
maxRuns = int(sys.argv[2])
timeout = int(sys.argv[3])
js = sys.argv[4]
gcdaDir = sys.argv[5]
gcovDir = sys.argv[6]
objDir = sys.argv[7]

printInterval = 10
failures = 0

swarm = "--noSwarm" not in sys.argv
subprocess.call(["rm -rf " + gcdaDir + "/*.gcda"], shell=True)

n = 1

startTime = time.time()
print "STARTING AT", startTime

elapsed = 0.0

while (n != (maxRuns+1)) and (elapsed < timeout):
    elapsed = time.time() - startTime
    if (n % printInterval) == 0: 
        print "TEST " + str(n), "; ELAPSED:", elapsed, "FAILURES:", failures
    
    testCase = prefix + ".tc" + str(n)

    # First, create the swarmed generator
    cName = testCase + "gen.js"
    cfName = testCase + ".conf"

    if swarm:
        subprocess.call(["python swarmup.py jsfunswarm.js " + cName + " " + cfName], shell=True)
    else:
        subprocess.call(["cp jsfunswarm.js " + cName], shell=True)

    # Generate test case
    subprocess.call([js + " " + cName + " >& " + testCase], shell=True)

    subprocess.call(["cp jsfunrun.js run.js"], shell=True)
    subprocess.call(["grep tryItOut " + testCase + " >> run.js"], shell=True)
    subprocess.call(["echo \"dumpln(\\\"ALL OK\\\");\" >> run.js"], shell=True)

    runTest.runTest(js)

    status = subprocess.call(["grep \"ALL OK\" run.out >& /dev/null"], shell=True)

    if (status != 0):
        print "TEST",n,"FAILED"
        failures += 1
        subprocess.call(["cp run.out " + testCase + ".out"],shell=True)
    subprocess.call(["rm", cName])
    #subprocess.call(["rm", cfName])
    subprocess.call(["rm","run.js"])
    subprocess.call(["rm","run.out"])
    subprocess.call(["mv",testCase,testCase+".test"])
    n = n + 1

(bcov, lcov, fcov) = coverage.getCoverage(gcovDir, objDir, True, prefix)

print "TOTAL TESTS: ", n-1
print "TOTAL FAILURES: ", failures
print "FUNCTION COVERAGE: ", len(fcov)
print "LINE COVERAGE: ", len(lcov)
print "BRANCH COVERAGE: ", len(bcov)

