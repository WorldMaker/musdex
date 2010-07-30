========
Commands
========

.. program:: musdex

``musdex`` is composed of a trio of subcommands, and one handy shortcut.
With no arguments provided, ``musdex`` defaults to its incremental
extraction tool.

.. program:: xedsum

The "boozniked" inverse ``xedsum`` similarly defaults to the incremental
combination tool.

Output Verbosity
================

.. program:: musdex
.. cmdoption:: -v, --verbose
.. cmdoption:: -q, --quiet

``musdex --verbose`` (or ``-v``) will print additional debugging
information, and ``musdex --quiet`` (or ``-q``) will print only warnings
and errors. These arguments need to be provided prior to the subcommand
name.

``musdex add``
==============

.. program:: musdex add

``musdex add`` adds one or more archives into the documentation
repository.

It performs a first extraction and adds all component files into the
VCS.

.. cmdoption:: --handler

The ``--handler`` option can be used to provide the Python dotted module
path to a custom handler for this archive. The default
(``ZipArchiveHandler``) should be sufficient in most cases. (For more
information about custom archive handlers see :doc:`handlers`.)

.. cmdoption:: --new

The ``--new`` option is used to create a new archive. ``musdex`` will
attempt to create it by forcing a combination of an empty archive. This
is an advanced option that may not work with all file formats/handlers.

``musdex remove``
=================

.. program:: musdex remove

``musdex remove`` removes one or more archives from the documentation
repository and VCS control.

``musdex extract``
==================

.. program:: musdex extract

``musdex extract`` runs through the archives under the musdex
documentation repository (or a subset thereof if archives are provided
as arguments) and extracts them as necessary.

By default, ``musdex extract`` runs in an *incremental* mode, whereby it
examines the archives, compares them to their last know modification
times and extracts only the ones that have been recently modified. It
additionally works to only extract the component parts themselves that
have been modified.

.. cmdoption:: -f, --force

The ``--force`` (or ``-f``) option can be provided to force ``musdex``
to extract (or re-extract) every file in every archive (or a subset
thereof, if other arguments are provided).

``musdex combine``
==================

.. program:: musdex combine

``musdex combine`` runs through the files under version control related
to the archives in the musdex documentation repository (or a subset of
such archives, if they are provided as arguments), and combines them as
necessary.

By default, ``musdex combine`` runs in an *incremental* mode, whereby it
compares the version control files to the last modification timestamps
when they were extracted. If files have changed it will combine (or more
likely re-combine) all of the necessary files to create an updated
version of the respective archive.

``musdex combine`` will, by default, make a backup for each archive
prior to attempting combination and clean up its backup after a
successful combination. (This behavior can be modified in the
:doc:`config`.)

.. cmdoption:: -f, --force

The ``--force`` (or ``-f``) option can be provided to force ``musdex``
to, regardless of timestamps, combine (or re-combine) every archive (or
a subset thereof, if other arguments are provided).

.. vim: ai spell tw=72
