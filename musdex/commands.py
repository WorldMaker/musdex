# VCS routines for musdex
#
# Copyright 2010 Max Battcher. Some rights reserved.
# Licensed for use under the Ms-RL. See attached LICENSE file.
from config import BASEDIR, load_index, save_index, save_config
import datetime
import logging
import os.path
import sys
import time
import zipfile

import vcs

def _datetime_from_epoch(epoch):
    return datetime.datetime(*time.localtime(epoch)[:6])

def add(args, config):
    index = load_index(config)
    for archive in args.archive:
        archive = os.path.relpath(archive)
        if 'archives' in config \
        and any(arc['filename'] == archive for arc in config['archives']):
            logging.warn("Archive already configured: %s" % archive)
            continue

        # TODO: Support other archive formats
        if not zipfile.is_zipfile(archive):
            logging.error("Not an archive: %s" % archive)
            continue

        logging.info("Extracting archive for the first time: %s" % archive)
        arcloc = os.path.join(BASEDIR, archive)
        ziparchive = zipfile.ZipFile(archive)
        ziparchive.extractall(arcloc)
        index[arcloc] = _datetime_from_epoch(os.path.getmtime(archive))

        logging.info("Adding archive to the VCS: %s" % archive)
        for info in ziparchive.infolist():
            path = os.path.relpath(os.path.join(BASEDIR, archive, info.filename))
            vcs.add_file(config, path)
            index[path] = datetime.datetime(*info.date_time)

        if 'archives' not in config: config['archives'] = []
        config['archives'].append({'filename': archive})
    save_config(args, config)
    save_index(config, index)

def extract(args, config):
    index = load_index(config)
    index_updated = False

    if args.archive: args.archive = map(os.path.relpath, args.archive)

    manifest = vcs.manifest(config)

    for archive in config['archives']:
        arcf = archive['filename']
        arcloc = os.path.join(BASEDIR, arcf)
        if args.archive and arcf not in args.archive:
            continue

        if args.force or arcloc not in index:
            logging.info("Extracting all of %s" % arcf)
            ziparchive = zipfile.ZipFile(arcf)
            ziparchive.extractall(arcloc)
            index[arcloc] = _datetime_from_epoch(os.path.getmtime(arcf))
            index_updated = True

            logging.info("Updating index for %s" % arcf)
            for info in ziparchive.infolist():
                path = os.path.relpath(os.path.join(arcloc, info.filename))
                # TODO: More efficient manifest check?
                if path not in manifest: vcs.add_file(config, path)
                index[path] = datetime.datetime(*info.date_time)
        else:
            logging.debug("Testing for extraction: %s" % arcf)
            lastmod = _datetime_from_epoch(os.path.getmtime(arcf))
            if lastmod > index[arcloc]:
                logging.info("Selectively extracting %s" % arcf)
                ziparchive = zipfile.ZipFile(arcf)
                index[arcloc] = _datetime_from_epoch(os.path.getmtime(arcf))
                index_updated = True

                for info in ziparchive.infolist():
                    path = os.path.relpath(os.path.join(arcloc, info.filename))
                    # TODO: More efficient manifest check?
                    if path not in manifest:
                        logging.debug("Extracting new file %s" % path)
                        ziparchive.extract(info, arcloc)
                        vcs.add_file(config, path)
                        index[path] = datetime.datetime(*info.date_time)
                    elif path not in index \
                    or datetime.datetime(*info.date_time) > index[path]:
                        logging.debug("Extracting updated file %s" % path)
                        ziparchive.extract(info, arcloc)
                        index[path] = datetime.datetime(*info.date_time)
            
    if index_updated: save_index(config, index)

def combine(args, config):
    index = load_index(config)
    index_updated = False

    if args.archive: args.archive = map(os.path.relpath, args.archive)

    manifest = vcs.manifest(config)

    for archive in config['archives']:
        combine = False
        arcf = archive['filename']
        arcloc = os.path.join(BASEDIR, arcf)
        if args.archive and arcf not in args.archive:
            continue

        if args.force or arcloc not in index:
            combine = True
        else:
            logging.debug("Checking modification times for %s" % arcf)
            for file in manifest:
                if file.startswith(arcloc):
                    if file not in index:
                        combine = True
                        break
                    lastmod = _datetime_from_epoch(os.path.getmtime(file))
                    if lastmod > index[file]:
                        combine = True
                        break
                    # TODO: Check for deleted files?
            
        if combine:
            logging.info("Combining %s" % arcf)
            index_updated = True
            ziparchive = zipfile.ZipFile(arcf, 'w', zipfile.ZIP_DEFLATED)
            for file in manifest:
                if file.startswith(arcloc):
                    index[file] = _datetime_from_epoch(os.path.getmtime(file))
                    ziparchive.write(file, os.path.relpath(file, arcloc))
            ziparchive.close()
            index[arcloc] = _datetime_from_epoch(os.path.getmtime(arcf))

    if index_updated: save_index(config, index)

# vim: ai et ts=4 sts=4 sw=4
