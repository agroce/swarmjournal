import glob



swarmData = []
noswarmData = []

f = "swarm.cov.71"
n = 0
for l in open(f):
    n = n + 10
    ls = l.split(",")
    record = {}
    record["n"] = str(n)
    record["lcov"] = ls[0]
    record["bcov"] = ls[1]
    record["ntests"] = ls[2][:-1]
    swarmData.append(record)

f = "nonswarm.cov.71"
n = 0
for l in open(f):
    n = n + 10
    ls = l.split(",")
    record = {}
    record["n"] = str(n)
    record["lcov"] = ls[0]
    record["bcov"] = ls[1]
    record["ntests"] = ls[2][:-1]
    noswarmData.append(record)    

n = 0
for l in open("mukill"):
    [nonswarm,swarm] = l.split(",")
    swarmData[n]["mut"] = swarm[:-1]
    noswarmData[n]["mut"] = nonswarm
    n = n + 1

f = open("swarm.data",'w')
f.write ("# 1 ntests 2 bcov 3 lcov 4\n")

for r in swarmData:
    f.write(r["n"] + " " + r["ntests"] + " " + r["bcov"] + " " + r["lcov"] + " " + r["mut"] + "\n")

f.close()

f = open("noswarm.data",'w')
f.write ("# 1 ntests 2 bcov 3 lcov 4\n")

for r in noswarmData:
    f.write(r["n"] + " " + r["ntests"] + " " + r["bcov"] + " " + r["lcov"] + " " + r["mut"] + "\n")

f.close()
