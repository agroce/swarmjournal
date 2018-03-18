import subprocess
import time
import os
import signal

def runTest(js, test="run.js", out="run.out", timeout=20):
    start = time.time()
    elapsed = time.time() - start
    p = subprocess.Popen(["script -c \"limit cputime " + str(timeout) + " ; " + js + " " + test + "\" " + out + " >& /dev/null"], shell=True)
    while (p.poll() is None) and (elapsed < timeout):
        elapsed = time.time() - start
    if (p.poll() is None):
        print "TERMINATING"
        os.kill(p.pid, signal.SIGKILL)
    return p.returncode
