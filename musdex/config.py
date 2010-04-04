# Configuration system for musdex
#
# Copyright 2010 Max Battcher. Some rights reserved.
# Licensed for use under the Ms-RL. See attached LICENSE file.
import logging
import os
import os.path
import yaml

import vcs

BASEDIR = "_musdex"
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
        logging.info("Config directory does not exist: %s" % confdir)
        os.makedirs(confdir)
    new_conf = not os.path.exists(conf)
    f = open(conf, 'w')
    yaml.dump(config, f)
    f.close()
    if new_conf:
        logging.info("Adding new configuration file to vcs: %s" % conf)
        vcs.add_file(config, conf)

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
        os.makedirs(idxdir)
    f = open(idx, 'w')
    yaml.dump(index, f)
    f.close()

# vim: ai et ts=4 sts=4 sw=4
