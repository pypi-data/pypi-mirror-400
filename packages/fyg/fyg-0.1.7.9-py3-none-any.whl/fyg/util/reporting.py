import os, sys
from datetime import datetime

LOG_FILE = None
ERROR_CB = None
TIME_CBS = {}
ON_LOG = []

def start_timer(tname):
    TIME_CBS[tname] = datetime.now()

def end_timer(tname, msg=""):
    diff = datetime.now() - TIME_CBS[tname]
    log("[timer] Completed in %s |%s| %s"%(diff, msg, tname), important=True)

def set_log(fname):
    global LOG_FILE
    LOG_FILE = open(fname, "a")

def on_log(cb):
    ON_LOG.append(cb)

def close_log():
    global LOG_FILE
    from ..config import config
    if LOG_FILE:
        LOG_FILE.close()
        LOG_FILE = None
    config.log.deep and closedeeps()

DLZ = {}

def closedeeps():
    for group in DLZ:
        for dl in DLZ[group]:
            DLZ[group][dl].close()
        del DLZ[group]

def deeplog(group, sub):
    gpath = os.path.join("logs", group)
    if group not in DLZ:
        DLZ[group] = {}
    if sub not in DLZ[group]:
        if "(" in sub:
            variety, name = sub[:-1].split("(")
            gpath = os.path.join(gpath, variety)
        else:
            name = sub
        if not os.path.exists(gpath):
            log("new directory: %s"%(gpath,), 2)
            os.makedirs(gpath)
        fullp = os.path.join(gpath,
            "%s.log"%(''.join([s for s in name if s.isalnum()]),))
        print("initializing", fullp)
        DLZ[group][sub] = open(fullp, "a")
    return DLZ[group][sub]

def basiclog(*msg):
    log(" ".join([str(m) for m in msg]))

def log(msg, level=0, important=False, group=None, sub=None):
    from ..config import config
    lcfg = config.log
    s = "%s%s"%("  " * level, msg)
    if lcfg.timestamp:
        s = "* %s : %s"%(datetime.now(), s)
    if important:
        s = "\n%s"%(s,)
    ws = "%s\n"%(s,)
    if LOG_FILE:
        LOG_FILE.write(ws)
        lcfg.flush and LOG_FILE.flush()
    if group and sub and lcfg.deep:
        dl = deeplog(group, sub)
        dl.write(ws)
        lcfg.flush and dl.flush()
    for cb in ON_LOG:
        cb(s)
    print(s)

def set_error(f):
    global ERROR_CB
    ERROR_CB = f

def error(msg, *lines):
    log("error: %s"%(msg,), important=True)
    for line in lines:
        log(line, 1)
    log("goodbye")
    if ERROR_CB:
        ERROR_CB(msg)
    else:
        sys.exit()