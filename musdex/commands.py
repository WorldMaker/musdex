"""
musdex commands
"""
# Copyright 2010 Max Battcher. Some rights reserved.
# Licensed for use under the Ms-RL. See attached LICENSE file.
import datetime
import logging
import os
import os.path
import re
import shutil
import time

from .config import BASEDIR, load_index, save_index, save_config
from .formatters import get_formatter
from .handlers import get_handler
from . import vcs

def _mtime(filename):
    return datetime.datetime(*time.localtime(os.path.getmtime(filename))[:6])

def add(args, config):
    """
    Add a file for tracking by musdex
    """
    index = load_index(config)

    for archive in args.archive:
        archive = os.path.relpath(archive)
        if 'archives' in config \
        and any(arc['filename'] == archive for arc in config['archives']):
            logging.warning("Archive already configured: %s", archive)
            continue

        handler = get_handler(args.handler)
        arcloc = os.path.join(BASEDIR, archive)
        arch = handler(archive, arcloc)
        if args.new:
            if not os.path.exists(arcloc):
                os.makedirs(arcloc)
                vcs.add_file(config, arcloc)
            for filename, timestamp in arch.combine(force=True):
                index[filename] = timestamp
        else:
            if not arch.check():
                logging.error("Archive not supported by given handler: %s: %s",
                              args.handler, archive)
                continue

            logging.info("Extracting archive for the first time: %s", archive)
            files = arch.extract(force=True)
            for filename, timestamp in files:
                index[filename] = timestamp
                if filename != arcloc:
                    vcs.add_file(config, filename)

        entry = {'filename': archive}
        if args.handler:
            entry['handler'] = args.handler
        if 'archives' not in config:
            config['archives'] = []
        config['archives'].append(entry)

    save_config(args, config)
    save_index(config, index)

def remove(args, config):
    """
    Remove a file from consideration by musdex
    """
    index = load_index(config)

    if 'archives' not in config:
        logging.error("No archives have been configured.")
        return

    manifest = vcs.manifest(config)

    for archive in args.archive:
        archive = os.path.relpath(archive)
        arcloc = os.path.join(BASEDIR, archive)

        if not any(arc['filename'] == archive for arc in config['archives']):
            logging.warning("Archive not configured: %s", archive)
            continue

        logging.info("Removing archive files from VCS.")
        for filename in manifest:
            if filename.startswith(arcloc):
                vcs.remove_file(config, filename)

                if filename in index:
                    del index[filename]

        config['archives'] = [arc for arc in config['archives'] \
            if arc['filename'] != archive]

    save_config(args, config)
    save_index(config, index)

def extract(args, config):
    """
    Extract musdex tracked archive files
    """
    index = load_index(config)
    index_updated = False

    fmts = []
    if 'post_extract' in config:
        logging.debug("Compiling post-extraction regular expressions")
        fmts = [(re.compile(regex), get_formatter(fname)) \
            for regex, fname in config['post_extract']]

    if args.archive:
        args.archive = map(os.path.relpath, args.archive)

    manifest = vcs.manifest(config)

    for archive in config['archives']:
        arcf = archive['filename']
        arcloc = os.path.join(BASEDIR, arcf)
        if args.archive and arcf not in args.archive:
            continue

        # Check if up to date
        if not args.force and arcloc in index \
        and _mtime(arcf) <= index[arcloc]:
            continue

        arcman = dict((f, index[f] if f in index else None) \
            for f in manifest if f.startswith(arcloc))

        hname = archive['handler'] if 'handler' in archive else None
        handler = get_handler(hname)
        arch = handler(arcf, arcloc, manifest=arcman)
        files = arch.extract(force=args.force or arcloc not in index)
        if files:
            index_updated = True

        for filename, timestamp in files:
            if timestamp is None: # File was removed
                del index[filename]
                vcs.remove_file(config, filename)
                continue
            index[filename] = timestamp
            for regex, fmt in fmts: # post-extract formatters
                if regex.match(filename):
                    logging.debug("Post-extraction: %s(%s)", fmt, filename)
                    fmt(filename)
            if filename != arcloc and filename not in arcman:
                vcs.add_file(config, filename)

    if index_updated:
        save_index(config, index)

def combine(args, config):
    """
    Combine musdex tracked index files
    """
    index = load_index(config)
    index_updated = False

    if args.archive:
        args.archive = map(os.path.relpath, args.archive)

    manifest = vcs.manifest(config)

    for archive in config['archives']:
        arcf = archive['filename']
        arcloc = os.path.join(BASEDIR, arcf)
        if args.archive and arcf not in args.archive:
            continue

        arcman = dict((f, index[f] if f in index else None) \
            for f in manifest if f.startswith(arcloc))

        logging.debug("Checking modification times for %s", arcf)
        # Unless forced or first-time combination, we do a quick sanity
        # check to see if any of the archive's files have changed
        if not args.force and arcloc in index and not \
        any(_mtime(f) > arcman[f] if arcman[f] is not None else True \
        for f in arcman):
            continue

        bakfilename = None
        if ('backup' not in config or config['backup']) \
        and os.path.exists(arcf):
            logging.debug('Backing up %s', arcf)
            bakfilename = arcf + '.bak~'
            shutil.copyfile(arcf, bakfilename)

        hname = archive['handler'] if 'handler' in archive else None
        handler = get_handler(hname)
        arch = handler(arcf, arcloc, manifest=arcman)
        files = arch.combine(force=args.force or arcloc not in index)
        if files:
            index_updated = True

        for filename, timestamp in files:
            index[filename] = timestamp

        if bakfilename is not None and ('leave_backups' not in config
                                        or not config['leave_backups']):
            logging.debug('Removing backup %s', bakfilename)
            os.remove(bakfilename)

    if index_updated:
        save_index(config, index)

# vim: ai et ts=4 sts=4 sw=4
