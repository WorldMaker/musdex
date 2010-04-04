==========
Formatters
==========

Formatters are Python call-ables that accept a filename and are expected
to perform some operation upon that file. Currently ``musdex`` only
supports post-extraction formatters. Formatters are expected to be
"lossy", and no formatters are enabled by default.

To enable a formatter, you append the post-extraction key to your
``musdex`` config file. This key is expected to be a list of tuples of a
regex and a Python dotted path. The regex will be matched against the
extracted filenames and those that match the regex will then be sent to
the formatter described by the Python dotted path.

An example of the post-extraction key in a config file, using the
built-in formatters:

.. sourcecode:: yaml

   post_extract:
     - [^.*\.xml$, xmllint]
     - [^.*\.html$, removecrs]

.. warning::
  
   Because filters may be sometimes "lossy", if not "destructive", it
   probably makes sense to use the strongest, explicit regular
   expressions that you are comfortable with when using formatters.

``xmllint``
===========

The ``xmllint`` formatter (``musdex.formatters.xmllint``) runs the file
through ``xmllint --format`` (a tool provided by ``libxml2``, thus
available for most platforms and provided by default by many unix-like
systems). This is useful as a "de-minifier" for minified XML documents,
such as those used by the ``.docx`` and ``.odt`` formats.

This formatter is useful in creating interestingly meaningful diffs from
embedded XML documents by inserting standardized lines/indentation into
an XML document. Because XML primarily ignores lines/indentation, most
applications that use XML (correctly) should have no issues dealing with
XML files that have been reformatted by ``xmllint``.

``remove_carriage_returns``
===========================

The ``removecrs`` formatter
(``musdex.formatters.remove_carriage_returns``) is one of the simplest
possible solutions to deal with the issue of cross-platform line ending
issues. This formatter simply removes all carriage returns (``"\r"``) it
comes across.

This should convert all Windows line endings (``"\r\n"``) to Unix line
endings (``"\n"``). Many programs that output platform-specific line
endings, often happily accept Unix line endings all the same. This is
the simplest way to standardize on using only Unix line endings in the
VCS/diffs.

Of course, this formatter is not for use for any format that may
explicitly require carriage returns.

.. vim: ai spell tw=72
