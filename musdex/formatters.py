"""
File post-extraction formatters for musdex
"""
# Copyright 2010 Max Battcher. Some rights reserved.
# Licensed for use under the Ms-RL. See attached LICENSE file.
import importlib
import logging
import os
import os.path
import sys
import subprocess

def xmllint(filename):
    """
    Pass file to xmllint command line tool
    """
    subprocess.call(['xmllint', '--format', '--output', filename, filename])

def remove_carriage_returns(filename):
    """
    Remove carriage returns (\r) from file
    """
    bakfile = "%s.bak~" % filename
    os.rename(filename, bakfile)
    inf = open(bakfile, 'rb')
    outf = open(filename, 'wb')
    for line in inf:
        outf.write(line.replace('\r', ''))
    inf.close()
    outf.close()
    os.remove(bakfile)

FORMATTER_CACHE = {'xmllint': xmllint, 'removecrs': remove_carriage_returns}

def get_formatter(name=None):
    """
    Find a formatter of a given name
    """
    if name is None:
        return
    elif name not in FORMATTER_CACHE:
        logging.debug('Importing formatter: %s', name)
        pieces = name.rsplit('.', 1)
        _temp = None
        try:
            _temp = importlib.import_module(pieces[0])
        except ImportError:
            logging.warning('Adding current directory to search path for formatter: %s', name)
            sys.path.append(os.getcwd())
            _temp = importlib.import_module(pieces[0])
        FORMATTER_CACHE[name] = getattr(_temp, pieces[1])
    return FORMATTER_CACHE[name]

# vim: ai et ts=4 sts=4 sw=4
