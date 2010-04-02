# VCS routines for musdex
#
# Copyright 2010 Max Battcher. Some rights reserved.
# Licensed for use under the Ms-RL. See attached LICENSE file.
from subprocess import CalledProcessError, PIPE, Popen, check_call
import logging
import os.path

DARCS_ADD = 'darcs add'
DARCS_SHOW_FILES = 'darcs show files --no-directories'

def manifest(config):
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

def add_file(config, file):
    logging.debug("Adding %s" % file)
    cmd = config["vcs_add"] if "vcs_add" in config else DARCS_ADD
    cmd = cmd.split(' ')
    cmd.append(file)
    check_call(cmd)

# vim: ai et ts=4 sts=4 sw=4
