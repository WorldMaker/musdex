"""
VCS routines for musdex
"""
# Copyright 2010 Max Battcher. Some rights reserved.
# Licensed for use under the Ms-RL. See attached LICENSE file.
from subprocess import check_call, check_output
import logging

DARCS_ADD = 'darcs add'
DARCS_REMOVE = 'darcs remove'
DARCS_SHOW_FILES = 'darcs show files --no-directories'

def manifest(config):
    """
    Load the manifest of files stored in version control
    """
    logging.debug("Loading manifest")
    cmd = config["vcs_show_files"] if "vcs_show_files" in config \
        else DARCS_SHOW_FILES
    cmd = cmd.split(' ')
    output = check_output(cmd, universal_newlines=True)

    # ASSUME: Broken by newlines with no filenames with newlines
    return (f for f in output.splitlines() if f)

def add_file(config, file):
    """
    Add a file to version control
    """
    logging.debug("Adding %s", file)
    cmd = config["vcs_add"] if "vcs_add" in config else DARCS_ADD
    cmd = cmd.split(' ')
    cmd.append(file)
    check_call(cmd)

def remove_file(config, file):
    """
    Remove a file from version control
    """
    logging.debug("Removing %s", file)
    cmd = config["vcs_remove"] if "vcs_remove" in config else DARCS_REMOVE
    cmd = cmd.split(' ')
    cmd.append(file)
    check_call(cmd)

# vim: ai et ts=4 sts=4 sw=4
