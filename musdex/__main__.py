#!/usr/bin/python
# musdex - The Version Control-Aware Zip Archive Tool
# Named after a spell briefly mentioned in Sorcerer magazine
# But can also stand for "Multi-Unit Single-Document EXtractor"
#
# Copyright 2010 Max Battcher. Some rights reserved.
# Licensed for use under the Ms-RL. See attached LICENSE file.

"""
musdex
------

musdex is a VCS-aware zip archive tool

Current documentation site: http://pythonhosted.org/musdex/
"""

def main(booznik=False):
    """
    Parse command line arguments and pass to individual commands

    Booznik is a "reversed spell" in Zork lore and used to refer to when main
    has been called from the command line as "xedsum" rather than "musdex".
    """
    try:
        from .config import load_config
    except ImportError:
        from musdex.config import load_config
    try:
        from . import commands
    except ImportError:
        from musdex import commands
    import argparse
    import logging
    import sys

    parser = argparse.ArgumentParser(prog='musdex' if not booznik else 'xedsum')
    parser.add_argument('--config', '-c')
    parser.add_argument('--verbose', '-v', action="store_true", default=False)
    parser.add_argument('--quiet', '-q', action="store_true", default=False)
    subparsers = parser.add_subparsers()

    parser_extract = subparsers.add_parser('extract')
    parser_extract.add_argument('--force', '-f', action="store_true",
                                default=False)
    parser_extract.add_argument('archive', nargs='*')
    parser_extract.set_defaults(func=commands.extract)

    parser_combine = subparsers.add_parser('combine')
    parser_combine.add_argument('--force', '-f', action="store_true",
                                default=False)
    parser_combine.add_argument('archive', nargs='*')
    parser_combine.set_defaults(func=commands.combine)

    parser_add = subparsers.add_parser('add')
    parser_add.add_argument('--new', '-n', action="store_true",
                            default=False)
    parser_add.add_argument('--handler')
    parser_add.add_argument('archive', nargs='+')
    parser_add.set_defaults(func=commands.add)

    parser_remove = subparsers.add_parser('remove')
    parser_remove.add_argument('archive', nargs='+')
    parser_remove.set_defaults(func=commands.remove)

    args = sys.argv[1:]
    if not any(args):
        args = ['extract'] if not booznik else ['combine']
    args = parser.parse_args(args)
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    elif not args.quiet:
        logging.basicConfig(level=logging.INFO)
    config = load_config(args)
    args.func(args, config)

def xedsum():
    """
    Boozniked entry point to musdex
    """
    main(True)

if __name__ == "__main__":
    main()

# vim: ai et ts=4 sts=4 sw=4
