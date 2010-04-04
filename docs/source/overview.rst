========
Overview
========

Modern document formats are increasingly becoming zip archives of a
sequence of document components. This includes the current formats for
both major office suites: the Open Document Format and the Office
OpenXML format.

While a version control system could store these zip archives directly,
as zip archives they act as opaque binary states that don't take the
best advantage of version control tools, most of which are designed for
text.

``musdex`` is a tool to automate the process, in coordination with a
VCS, to keep in synchronization a zip-based document and its individual
components for use as assets to be kept under version control.

==========================
What Does ``musdex`` Mean?
==========================

``musdex`` is a magic spell tangentially referenced in the *Zork*
mythology, known for some sort of "body deformation". For those that
prefer acronyms (or more properly "backronyms"), you can consider
``musdex`` stands for "Multiple-Unit Single-Document EXtractor".

==================================
Getting Started Quickly With Darcs
==================================

.. highlight:: bash

``musdex`` defaults to speaking to darcs_ as a VCS. This is configurable
and will be discussed in detail elsewhere. This is a mini-tutorial for
getting started very quickly using the darcs-based defaults.

Start a new document repository and add your first document::

  $ darcs init
  $ musdex add ADocument.ext

``musdex`` will perform its first extraction of ``ADocument.ext`` into
its ``_musdex`` directory. It will also add all of the relevant files to
darcs. All you have to do to record the pieces of ``ADodument.ext`` is a
normal darcs record, such as::

  $ darcs rec -am "Added ADocument.ext"

.. note::

   For darcs in particular, you generally don't want to add any of the
   files that musdex explicitly skips: the original document itself, and
   the musdex hidden "index" file.

To keep the document automatically in sync, you can make use of darcs
hooks. It can be as simple as adding the following two lines to the
repository's ``_darcs/prefs/defaults`` file::

  record prehook musdex
  amend-record prehook musdex
  apply prehook musdex
  apply posthook xedsum
  pull prehook musdex
  pull posthook xedsum

This will automatically extract any changes from ``ADocument.ext``
so that they can be recorded, and recombine any changes that are pulled
in from other sources, all while you use darcs commands like normal.
After that ``musdex add`` is mostly the only direct ``musdex``
interaction you will need.

The only other thing to keep in mind would be that when using ``darcs
get`` to get new copies you will need to reconstruct the original
archives, which is a simple matter::

  $ darcs get orig new
  $ cd new
  $ musdex combine # or use the xedsum shortcut name

Don't forget to copy the lines into the new repository's
``_darcs/prefs/defaults``.

.. _darcs: http://darcs.net

.. vim: ai spell tw=72
