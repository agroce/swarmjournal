import subprocess
import os

def getCoverage(gcovDir, objDir, save=False, prefix=""):
    subprocess.call(["cd " + gcovDir + "; gcov *.c *.cpp -b -o " + objDir + ">& /dev/null"], shell=True)

    fcov = []
    lcov = []
    bcov = []
    gcovFiles = os.listdir(gcovDir)
    gcovFiles = sorted(gcovFiles)
    for f in gcovFiles:
        lastline = "BADLINE"
        if ".gcov" in f:
            for l in open(gcovDir + f):
                fs = l.split()
                if fs[0] == "function":
                    if int(fs[3]) > 0:
                        fcov.append(fs[1])
                elif fs[0] == "branch":
                    if "never" not in fs and "0%" not in fs:
                        perc = ""
                        for ps in fs:
                            if "%" in ps:
                                perc = ps[:-1]
                                bcov.append(f + ":" + lastline + ":b" + fs[1])
                elif fs[0] != "call":
                    ls = l.split(":")
                    ls0 = ls[0].split()[0]
                    ls1 = (ls[1].split()[0]).split(".gcov")[0]
                    lastline = ls1
                    if (ls0 != "-") and (ls0 != "#####"):
                        lcov.append(f.split(".gcov")[0] + ":" + ls1)

    if save:
        fcovFile = open(prefix + ".fcov",'w')
        bcovFile = open(prefix + ".bcov",'w')
        lcovFile = open(prefix + ".lcov",'w')

        for f in fcov:
            fcovFile.write(f + "\n")
        fcovFile.close()

        for b in bcov:
            bcovFile.write(b + "\n")
        bcovFile.close()

        for l in lcov:
            lcovFile.write(l + "\n")
        lcovFile.close()

    return (lcov, bcov, fcov)
