"""
File-type handlers for musdex
"""
# Copyright 2010 Max Battcher. Some rights reserved.
# Licensed for use under the Ms-RL. See attached LICENSE file.
import datetime
import importlib
import logging
import os.path
import sys
import time
import zipfile

def _datetime_from_epoch(epoch):
    return datetime.datetime(*time.localtime(epoch)[:6])

class ZipArchiveHandler(object):
    """
    ZipArchiveHandler combines and extract zip archives
    """

    def __init__(self, archive, location, manifest=None):
        self.archive = archive
        self.location = location
        self.manifest = manifest or {}

    def check(self):
        """
        Verify file is a zip file
        """
        return zipfile.is_zipfile(self.archive)

    def extract(self, force=False):
        """
        Extract zip file
        """
        manifestfiles = set(self.manifest.keys())
        if force:
            logging.info("Extracting all of %s", self.archive)
            ziparchive = zipfile.ZipFile(self.archive)
            ziparchive.extractall(self.location)

            for info in ziparchive.infolist():
                path = os.path.relpath(os.path.join(self.location,
                                                    info.filename))
                yield (path, datetime.datetime(*info.date_time))
                if path in manifestfiles:
                    manifestfiles.remove(path)
        else:
            logging.info("Selectively extracting %s", self.archive)
            ziparchive = zipfile.ZipFile(self.archive)

            for info in ziparchive.infolist():
                path = os.path.relpath(os.path.join(self.location,
                                                    info.filename))
                timestamp = datetime.datetime(*info.date_time)
                if path not in self.manifest:
                    logging.debug("Extracting new file %s", path)
                    ziparchive.extract(info, self.location)
                    yield (path, timestamp)
                elif timestamp > self.manifest[path]:
                    logging.debug("Extracting updated file %s", path)
                    ziparchive.extract(info, self.location)
                    yield (path, timestamp)
                if path in manifestfiles:
                    manifestfiles.remove(path)

        # Check for removed files
        if manifestfiles:
            for filename in manifestfiles:
                yield (filename, None)

        yield (self.location,
               _datetime_from_epoch(os.path.getmtime(self.archive)))

    def combine(self, force=False):
        """
        Combine zip file
        """
        # We can ignore force here, because zipfile doesn't have strong
        # support for incremental file updates so we are *always*
        # re-combining the entire file.
        logging.info("Combining %s", self.archive)
        ziparchive = zipfile.ZipFile(self.archive, 'w',
                                     zipfile.ZIP_DEFLATED)
        for file in self.manifest:
            ziparchive.write(file, os.path.relpath(file, self.location))
            yield (file, _datetime_from_epoch(os.path.getmtime(file)))
        ziparchive.close()
        yield (self.location,
               _datetime_from_epoch(os.path.getmtime(self.archive)))

HANDLER_CACHE = {'zip': ZipArchiveHandler}

def get_handler(handler_name=None):
    """
    Find a handler of a given name
    """
    if handler_name is None:
        return ZipArchiveHandler
    elif handler_name not in HANDLER_CACHE:
        logging.debug('Importing handler: %s', handler_name)
        pieces = handler_name.rsplit('.', 1)
        _temp = None
        try:
            _temp = importlib.import_module(pieces[0])
        except ImportError:
            logging.warning('Adding current directory to search path for handler: %s', handler_name)
            sys.path.append(os.getcwd())
            _temp = importlib.import_module(pieces[0])
        HANDLER_CACHE[handler_name] = getattr(_temp, pieces[1])
    return HANDLER_CACHE[handler_name]

# vim: ai et ts=4 sts=4 sw=4
