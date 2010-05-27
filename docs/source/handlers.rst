========
Handlers
========

Handlers are Python objects that are deferred to perform the actual
extraction/combination for an archive. By default, ``musdex`` uses the
``ZipArchiveHandler`` (``musdex.handlers.ZipArchiveHandler``), but
``musdex`` can be configured to use any handler a user specifies (via a
dotted Python path in the ``--handler`` argument to ``musdex add``, or
as a ``handler`` key in the ``archives`` section of the ``musdex``
configuration file).

Custom Handler Interface
------------------------

.. class:: Handler

Custom handlers should be somewhat straightforward to build. ``musdex``
itself handles all of the VCS communication and index-management,
leaving a handler to focus on extraction and combination. The interface
is a simple "duck-typed" interface and should be relatively straight
forward:

.. function:: __init__(self, archive, location, manifest={})

The handler is initialized with the path to the ``archive`` itself, as
well as the ``location`` for the extracted ``archive`` under the
``musdex`` repository. Depending on the command, the handler may also be
provided a ``manifest``. The ``manifest`` is a dictionary mapping
VCS-controlled filenames under the ``location`` and their most recent
timestamps (as ``datetime.datetime``, from the ``musdex`` index).

.. function:: check()

The handler is asked to check if the ``archive`` is in the expected
format to be handled by this handler. This is a sanity-check utilized by
``musdex add``.

.. function:: extract(self, force=False)

The handler is expected to extract files within the ``archive`` to the
``location``. If ``force`` is ``True``, the handler should extract every
file in the ``archive``. Otherwise, the handler should do its best to
only extract only those portions that have changed, using the
``manifest`` to determine recently changed operations.

The expected return value is a list of tuples for each file extracted
with the file path (under the ``location``) and the last modification
time (as a ``datetime.datetime`` object). Additionally, if anything is
expanded, there should be a tuple for the ``location`` itself, with the
last modification date of the ``archive`` itself.

The handler can return ``None`` as the last modification time for a file
path to indicate that a file was removed from the archive and should be
removed from the VCS.

.. function:: combine(self, force=False)

The handler is expected to combine files within the ``manifest`` (under
the ``location``) back into the ``archive``. If ``force`` is ``True``,
the handler should combine every file in the ``manifest``. Otherwise,
the handler should do its best to only recombine those portions that
have changed, using the timestamps in the ``manifest`` to determine
recently modified files.

The expected return value is similar to ``extract`` in that it should be
a list of tuples, one for each filename that was combined and its last
modification time (as a ``datetime.datetime`` object). Additionally, if
anything is combined, there should be a tuple for the ``location``
itself, with the last modification date of the recombined ``archive``.

.. vim: ai spell tw=72
