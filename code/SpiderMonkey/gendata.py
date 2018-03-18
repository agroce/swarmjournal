import subprocess
import sys

runtime = int(sys.argv[1])
maxRuns = int(sys.argv[2])
dir = sys.argv[3]
start = int(sys.argv[4])

run1_6 = ' "/scratch/js1.6/src/Linux_All_DBG.OBJ/js" "/scratch/js1.6/src/Linux_All_DBG.OBJ/" "/scratch/js1.6/src/" "Linux_All_DBG.OBJ" '
run1_7 = ' "/scratch/js1.7/src/Linux_All_DBG.OBJ/js" "/scratch/js1.7/src/Linux_All_DBG.OBJ/" "/scratch/js1.7/src/" "Linux_All_DBG.OBJ" '
run1_8_5 = '  "/scratch/js1.8/js/src/shell/js" "/scratch/js1.8/js/src/" "/scratch/js1.8/js/src/" "." '

verSet = [("js1.6", run1_6), ("js1.7", run1_7), ("js1.8.5", run1_8_5)]
expSet = [("swarm", ""), ("noswarm"," --noSwarm ")]

n = start
while (n < maxRuns):
    for (n1, cmdVer) in verSet:
        for (n2, cmdExp) in expSet:
            name = dir + "/" + n1 + "." + n2 + "." + str(n)
            print name
            subprocess.call(["mkdir",name])
            cmd = "python runtests.py "
            cmd += '"' + name + "/" + 't"'
            cmd += " -1 " + str(runtime)
            cmd += cmdVer
            cmd += cmdExp
            subprocess.call([cmd], shell=True)
            subprocess.call(["gzip " + name + "/*.test"], shell=True)
            subprocess.call(["gzip " + name + "/*.out"], shell=True)
    n += 1
