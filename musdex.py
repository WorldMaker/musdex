#!/usr/bin/python
# musdex - The Version Control-Aware Zip Archive Tool
# Named after a spell briefly mentioned in Sorcerer magazine
# But can also stand for "Multi-Unit Single-Document EXtractor"
#
# Copyright 2010 Max Battcher. Some rights reserved.
# Licensed for use under the Ms-RL. See attached LICENSE file.
from subprocess import CalledProcessError, PIPE, Popen, check_call
import argparse
import datetime
import logging
import os
import os.path
import sys
import time
import yaml
import zipfile

BASEDIR = "_musdex"
DARCS_ADD = 'darcs add'
DARCS_SHOW_FILES = 'darcs show files --no-directories'
DEFAULT_CONFIG = os.path.join(BASEDIR, "musdex.yaml")
DEFAULT_INDEX = os.path.join(BASEDIR, ".musdex.index.yaml")

def load_config(args):
    conf = DEFAULT_CONFIG
    if args.config:
        conf = args.config
    logging.debug("Loading configuration from %s" % conf)
    if not os.path.exists(conf):
        logging.info("No configuration file found at %s" % conf)
        return {}
    f = open(conf, 'r')
    config = yaml.load(f)
    f.close()
    return config

def save_config(args, config):
    conf = DEFAULT_CONFIG
    if args.config:
        conf = args.config
    logging.debug("Saving configuration to %s" % conf)
    confdir = os.path.dirname(conf)
    if confdir and not os.path.exists(confdir):
        loggin.info("Config directory does not exist: %s" % confdir)
        os.mkdirs(confdir)
    new_conf = not os.path.exists(conf)
    f = open(conf, 'w')
    yaml.dump(config, f)
    f.close()
    if new_conf:
        logging.info("Adding new configuration file to vcs: %s" % conf)
        vcs_add_file(config, conf)

# TODO: Perhaps the index should instead be a less verbose format?
def load_index(config):
    index = config['index'] if 'index' in config else DEFAULT_INDEX
    if os.path.exists(index):
        logging.debug("Loading existing index: %s" % index)
        f = open(index, 'r')
        index = yaml.load(f)
        f.close()
        return index
    return {}

def save_index(config, index):
    idx = config['index'] if 'index' in config else DEFAULT_INDEX
    logging.debug("Saving index: %s" % idx)
    idxdir = os.path.dirname(idx)
    if idxdir and not os.path.exists(idxdir):
        logging.info("Index directory does not exist: %s" % idxdir)
        os.mkdirs(idxdir)
    f = open(idx, 'w')
    yaml.dump(index, f)
    f.close()

def _datetime_from_epoch(epoch):
    return datetime.datetime(*time.localtime(epoch)[:6])

def vcs_manifest(config):
    logging.debug("Loading manifest")
    cmd = config["vcs_show_files"] if "vcs_show_files" in config \
        else DARCS_SHOW_FILES
    cmd = cmd.split(' ')
    pr = Popen(cmd, stdout=PIPE)
    manifest = pr.communicate()[0]
    if pr.returncode != 0:
        raise CalledProcessError(pr.returncode, cmd[0])

    # ASSUME: Broken by newlines with no filenames with newlines
    files = [os.path.relpath(f.strip()) for f in manifest.split('\n')
        if f.strip()]
    return files

def vcs_add_file(config, file):
    logging.debug("Adding %s" % file)
    cmd = config["vcs_add"] if "vcs_add" in config else DARCS_ADD
    cmd = cmd.split(' ')
    cmd.append(file)
    check_call(cmd)

def add(args):
    config = load_config(args)
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
            vcs_add_file(config, path)
            index[path] = datetime.datetime(*info.date_time)

        if 'archives' not in config: config['archives'] = []
        config['archives'].append({'filename': archive})
    save_config(args, config)
    save_index(config, index)

def extract(args):
    config = load_config(args)
    index = load_index(config)
    index_updated = False

    if args.archive: args.archive = map(os.path.relpath, args.archive)

    manifest = vcs_manifest(config)

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
                if path not in manifest: vcs_add_file(config, path)
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
                        vcs_add_file(config, path)
                        index[path] = datetime.datetime(*info.date_time)
                    elif path not in index \
                    or datetime.datetime(*info.date_time) > index[path]:
                        logging.debug("Extracting updated file %s" % path)
                        ziparchive.extract(info, arcloc)
                        index[path] = datetime.datetime(*info.date_time)
            
    if index_updated: save_index(config, index)

def combine(args):
    config = load_config(args)
    index = load_index(config)
    index_updated = False

    if args.archive: args.archive = map(os.path.relpath, args.archive)

    manifest = vcs_manifest(config)

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

def main(booznik=False):
    parser = argparse.ArgumentParser(prog='musdex' if not booznik else 'xedsum')
    parser.add_argument('--config', '-c')
    parser.add_argument('--verbose', '-v', action="store_true", default=False)
    parser.add_argument('--quiet', '-q', action="store_true", default=False)
    subparsers = parser.add_subparsers()

    parser_extract = subparsers.add_parser('extract')
    parser_extract.add_argument('--force', '-f', action="store_true",
        default=False)
    parser_extract.add_argument('archive', nargs='*')
    parser_extract.set_defaults(func=extract)
    
    parser_combine = subparsers.add_parser('combine')
    parser_combine.add_argument('--force', '-f', action="store_true",
        default=False)
    parser_combine.add_argument('archive', nargs='*')
    parser_combine.set_defaults(func=combine)

    parser_add = subparsers.add_parser('add')
    parser_add.add_argument('archive', nargs='+')
    parser_add.set_defaults(func=add)

    args = sys.argv[1:]
    if len(args) == 0:
        args = ['extract'] if not booznik else ['combine']
    args = parser.parse_args(args)
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    elif not args.quiet:
        logging.basicConfig(level=logging.INFO)
    args.func(args)

if __name__ == "__main__":
    main()

# vim: ai et ts=4 sts=4 sw=4
