# File-type handlers for musdex
#
# Copyright 2010 Max Battcher. Some rights reserved.
# Licensed for use under the Ms-RL. See attached LICENSE file.
import datetime
import logging
import os.path
import time
import zipfile

def _datetime_from_epoch(epoch):
    return datetime.datetime(*time.localtime(epoch)[:6])

class ZipArchiveHandler(object):
    def __init__(self, archive, location, manifest={}):
        self.archive = archive
        self.location = location
        self.manifest = manifest

    def check(self):
        return zipfile.is_zipfile(self.archive)

    def extract(self, force=False):
        manifestfiles = set(self.manifest.keys())
        if force:
            logging.info("Extracting all of %s" % self.archive)
            ziparchive = zipfile.ZipFile(self.archive)
            ziparchive.extractall(self.location)

            for info in ziparchive.infolist():
                path = os.path.relpath(os.path.join(self.location,
                    info.filename))
                yield (path, datetime.datetime(*info.date_time))
                if path in manifestfiles: manifestfiles.remove(path)
        else:
            logging.info("Selectively extracting %s" % self.archive)
            ziparchive = zipfile.ZipFile(self.archive)

            for info in ziparchive.infolist():
                path = os.path.relpath(os.path.join(self.location,
                    info.filename))
                time = datetime.datetime(*info.date_time)
                if path not in self.manifest:
                    logging.debug("Extracting new file %s" % path)
                    ziparchive.extract(info, self.location)
                    yield (path, time)
                elif time > self.manifest[path]:
                    logging.debug("Extracting updated file %s" % path)
                    ziparchive.extract(info, self.location)
                    yield (path, time)
                if path in manifestfiles: manifestfiles.remove(path)

        # Check for removed files
        if manifestfiles:
            for f in manifestfiles:
                yield (f, None)

        yield (self.location,
            _datetime_from_epoch(os.path.getmtime(self.archive)))

    def combine(self, force=False):           
        # We can ignore force here, because zipfile doesn't have strong
        # support for incremental file updates so we are *always*
        # re-combining the entire file.
        logging.info("Combining %s" % self.archive)
        ziparchive = zipfile.ZipFile(self.archive, 'w',
            zipfile.ZIP_DEFLATED)
        for file in self.manifest:
            ziparchive.write(file, os.path.relpath(file, self.location))
            yield (file, _datetime_from_epoch(os.path.getmtime(file)))
        ziparchive.close()
        yield (self.location, 
            _datetime_from_epoch(os.path.getmtime(self.archive)))

_handler_cache = {}

def get_handler(handler_name=None):
    if handler_name is None:
        return ZipArchiveHandler
    elif handler_name not in _handler_cache:
        pieces = handler_name.rsplit('.', 1)
        _temp = __import__(pieces[0],
            globals(),
            locals(),
            [pieces[1]],
            -1,
        )
        _handler_cache[handler_name] = getattr(_temp, pieces[1])
    return _handler_cache[handler_name]

# vim: ai et ts=4 sts=4 sw=4
