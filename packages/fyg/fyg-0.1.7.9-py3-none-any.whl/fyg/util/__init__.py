import os, subprocess, platform
from .io import read, write, writejson, ask, confirm, selnum
from .reporting import start_timer, end_timer, set_log, on_log, close_log, closedeeps, deeplog, basiclog, log, set_error, error

def rm(pname):
    if os.path.islink(pname):
        log("removing symlink: %s"%(pname,), 2)
        os.remove(pname)
    elif os.path.isdir(pname):
        log("removing folder: %s"%(pname,), 2)
        os.rmdir(pname)
    elif os.path.exists(pname):
        log("removing file: %s"%(pname,), 2)
        os.remove(pname)
    else:
        log("can't remove file (doesn't exist): %s"%(pname,), 2)

def indir(data, path):
    for f in [os.path.join(path, p) for p in os.listdir(path)]:
        if os.path.isfile(f) and data == read(f, binary=True):
            return os.path.split(f)[-1]

def batch(dlist, f, *args, **kwargs):
    chunk = kwargs.pop("chunk", 1000)
    i = 0
    while i < len(dlist):
        f(dlist[i:i+chunk], *args, **kwargs)
        i += chunk

def sudoed(cline, sudo=False):
    if sudo and platform.system() != "Windows" and os.geteuid(): # !root
        cline = "sudo %s"%(cline,)
    return cline

def cmd(cline, sudo=False, silent=False):
    cline = sudoed(cline, sudo)
    silent or log('issuing command: "%s"'%(cline,), 2)
    subprocess.call(cline, shell=True)

def output(cline, sudo=False, silent=False, loud=False):
    cline = sudoed(cline, sudo)
    silent or log('getting output for: "%s"'%(cline,), 2)
    output = subprocess.getoutput(cline)
    loud and log(output)
    return output

def pcount(pname):
    log("checking count: %s"%(pname,), important=True)
    num = int(output("ps -ef | grep %s | egrep -v 'screener|pcount|grep' | wc -l"%(pname,)))
    log("%s count: %s"%(pname, num), 1)
    return num

def pcheck(pname, target, starter):
    if target and pcount(pname) != target:
        log("not enough %s processes - restarting screen!"%(pname,), 1)
        log(output("screen -Q windows"), important=True)
        cmd("killall screen; %s"%(starter,))
        return True

def pkill(pname, force=False):
    pblock = output("ps -ef | grep %s | egrep -v 'screener|pkill|grep'"%(pname,))
    if not pblock:
        log("no '%s' processes!"%(pname,))
    else:
        plines = pblock.split("\n")
        log("found %s '%s' processes"%(len(plines), pname), important=True)
        if plines:
            procs = [[w for w in line.split(" ") if w][1] for line in plines]
            if force or confirm("kill %s '%s' processes"%(len(procs), pname)):
                for proc in procs:
                    cmd("kill -9 %s"%(proc,))
    log("goodbye")

class Loggy(object):
    def subsig(self):
        pass

    def sig(self):
        ss = self.subsig()
        sig = self.__class__.__name__
        return ss and "%s(%s)"%(sig, ss) or sig

    def log(self, *msg):
        basiclog(self.sig(), ":", *msg)

class Named(Loggy):
    def __init__(self, name):
        self.name = name

    def subsig(self):
        return self.name