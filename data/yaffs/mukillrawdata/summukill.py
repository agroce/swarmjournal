
import os,glob,re,sys

#----------------------------------------
def getCoverage():
    cov=dict()
    f=open('allcfiles','r')
    allcfiles=f.readlines()
    f.close()
    for cfile in allcfiles:
      cfile=cfile.strip()
      os.system('gcov %s'%(cfile))
      linecov=getLineCoverage(cfile+'.gcov')
      for c in linecov:
        s='%s@@%d'%(cfile,c)
        cov[s]=1
    return cov  	
#----------------------------------------
def getLineCoverage(filename):
    cov=set()
    if not os.path.exists(filename):
      return cov 	
    f = open(filename)
    lines = f.readlines()
    f.close()
    for line in lines:
        newline=line.strip()
        if len(newline) > 0:
            if newline[0] != '-' and newline[0] != '#':
                cov.add(int(newline.split(':')[1].strip()))
    return cov
#--------------------------------------------------------------	
def coveredmutant(im,cov):
	f=open('allmutants','r')
	lines=f.readlines()
	f.close()
	line=lines[im]
	line=line.strip()
	parts=re.split('@@',line)
	fname=parts[0]
	lineno=int(parts[1])
	covered=False
	ide='%s@@%d'%(fname,lineno)
	if ide in cov:
		covered=True
	return covered
#--------------------------------------------------------------	
def applymutant(im): # 0 based
	os.system('cp origcfiles/*.c ./')
	f=open('allmutants','r')
	lines=f.readlines()
	f.close()
	line=lines[im]
	line=line.strip()
	parts=re.split('@@',line)
	fname=parts[0]
	lineno=int(parts[1])
	newcontent=parts[2]
	
	f=open(fname,'r')
	lines=f.readlines()
	f.close()
	f=open(fname,'w')
	for (il,line) in enumerate(lines):
		if il==lineno-1:
			f.write(newcontent)
			f.write('\n')
		else:
			f.write(line)
	f.close()
#--------------------------------------------------------------	
def comparefile(fname1, fname2):
	same=False
	if os.path.exists(fname1) and os.path.exists(fname2):
		f=open(fname1,'rb')
		c1=f.read()
		f.close()
		f=open(fname2,'rb')
		c2=f.read()
		f.close()
		if c1==c2:
			same=True
	return same
#--------------------------------------------------------------	
def readtestcasesrange(fname):
	res=[]
	f=open(fname,'r')
	lines=f.readlines()
	for line in lines:
		line=line.strip()
		res.append(int(line.split(',')[2]))
	res1=[]
	for it,d in enumerate(res):
		if it==0:
			res1.append((0,d))
		else:
			res1.append((res[it-1],d))
	return res1
#--------------------------------------------------------------	
minmutants=100000
for segid in range(0,72):
	f=open('mukill_%d'%(segid),'r')
	lines=f.readlines()
	f.close()
	if len(lines)<minmutants:
		minmutants=len(lines)

swarm=[]
nonswarm=[]

for segid in range(0,72):
	swarm.append(set())
	nonswarm.append(set())

for segid in range(0,72):
	f=open('mukill_%d'%(segid),'r')
	lines=f.readlines()
	f.close()
	#lines=lines[0:minmutants]
	nonswarmkilled=[]
	swarmkilled=[]
	for m,line in enumerate(lines):
		line=line.strip()
		parts=line.split(';')
		assert(len(parts)==3)
		k1=int(parts[1].split(',')[0])
		if k1>0:
			swarmkilled.append(m)
		k2=int(parts[2].split(',')[0])
		if k2>0:
			nonswarmkilled.append(m)
	nonswarm[segid]=set(nonswarmkilled)
	swarm[segid]=set(swarmkilled)		


f=open('mukill','w')
f2=open('mukill.10min','w')
s1=set()
s2=set()
for si,s in enumerate(swarm):
	f2.write('%d,%d\n'%(len(s),len(nonswarm[si])))
	s1|=s
	s2|=nonswarm[si]
	f.write('%d,%d\n'%(len(s1),len(s2)))
f.close()
f2.close()

