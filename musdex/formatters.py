# File post-extraction formatters for musdex
#
# Copyright 2010 Max Battcher. Some rights reserved.
# Licensed for use under the Ms-RL. See attached LICENSE file.
import subprocess

def xmllint(filename):
    subprocess.call(['xmllint', '--format', '--output', filename, filename])

def remove_carriage_returns(filename):
    import os
    bakfile = "%s.bak~" % filename
    os.rename(filename, bakfile)
    inf = open(bakfile, 'rb')
    outf = open(filename, 'wb')
    for line in inf:
        outf.write(line.replace('\r', ''))
    inf.close()
    outf.close()
    os.remove(bakfile)

_fmt_cache = {'xmllint': xmllint, 'removecrs': remove_carriage_returns}

def get_formatter(name=None):
    if name is None:
        return
    elif name not in _fmt_cache:
        pieces = name.rsplit('.', 1)
        _temp = __import__(pieces[0],
            globals(),
            locals(),
            [pieces[1]],
            -1,
        )
        _fmt_cache[name] = getattr(_temp, pieces[1])
    return _fmt_cache[name]

# vim: ai et ts=4 sts=4 sw=4
