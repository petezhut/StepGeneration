#!/usr/bin/env python

import os
import sys
import itertools

STEP_NAMES = "Given When Then".split()

def buildSteps(data):
    rem = []
    if len(data) < 2:
        return data
    try:
        for check in [a for a in itertools.combinations_with_replacement(data, 2)]:
            a = check[0].split()
            b = check[1].split()
            new = []
            for x in range(len(a)):
                new.append(a[x]) if a[x] == b[x] else new.append("(\%s" % ("w+.*)"))
            if " ".join(new) not in data:
                data.append(" ".join(new))
            if " ".join(a) not in rem:
                rem.append(" ".join(a))
            if " ".join(b) not in rem:
                rem.append(" ".join(b))
        for a in rem: del data[data.index(a)]
        return data
    finally:
        return data

def returnSteps(feature, name):
    with open(feature, 'rb') as f:
        lines = f.readlines()
    ret = []
    for a in filter(None, [a.strip() for a in lines]):
        if a.startswith(name) and a not in ret:
            x = a.split()
            ret.append(a)
    return buildSteps(ret)

def writeOut(data, fname='teststeps.py'):
    if os.path.isfile(fname): os.remove(fname)
    with open(fname, 'ab') as f:
        f.write("\n".join(["from freshen import %s" % (a) for a in data['head']]))
        f.write("\n\n\n")
        f.write("@Before\ndef before(sc):\n\tpass\n\n")
        f.write("@After\ndef after(sc):\n\tpass\n\n")
        for count, step in enumerate(data['steps']):
            x = step.split()
            fargs = ", ".join(map(lambda x: "arg%d" % (x), range(len(filter(lambda x: x == '(\w+.*)', x)))))
            f.write('@%s("%s")\n' % (x[0], " ".join(x[1:])))
            f.write("def step%d(%s):\n\tpass\n\n" % (count, fargs))

def updateFeature(fname):
    f = open(fname, 'rb')
    lines = filter(None, map(lambda x: x.rstrip(), f.readlines()))
    f.close()
    lines.insert(0, "Using step definitions from: '%s'\n" % (os.path.basename(fname).split(".feature")[0]))
    with open(fname, 'wb') as f:
        f.write("\n".join(lines))

if __name__ == '__main__':
    if len(sys.argv) == 2:
        try:
            feature = os.path.realpath(sys.argv[1])
            data = {'head' : "Before After scc".split(), 'steps' : []} 
            for a in STEP_NAMES:
                ret = returnSteps(feature, a)
                if len(ret) > 0:
                    data['steps'].extend(ret)
                if a not in data['head']:
                    data['head'].append(a)
            writeOut(data, "%s.py" % (os.path.basename(feature).split(".feature")[0]))
            updateFeature(feature)
        except Exception, e:
            print(str(e))
            sys.exit()
