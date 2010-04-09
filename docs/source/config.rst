==================
Configuration File
==================

``musdex`` has one important configuration file, which defaults to
``_musdex/musdex.yaml``. This is a yaml_ file that is expected to be
version controlled. The full specification of this file is currently:

.. sourcecode:: yaml

   vcs_add: vcstool command-to-add-a-file # default: darcs add
   vcs_show_files: vcstool list-of-files # default: darcs show files
   backup: yes # create backups before calling combination handlers
   leave_backups: no # remove backups after successful combination
   index: path/to/.musdex.index.yaml # default: _musdex/.musdex.index.yaml
   archives:
     - filename: archive1.zip
     - filename: path/to/archive2.docx
     - filename: archive3.odt
     - filename: archive4.celtx
     - filename: archive5.custom
       handler: custom.CustomHandler # archive handler
   post_extract: # post-extraction formatters
     - [.*\.xml, xmllint]
     - [.*\.html, removecrs]
     - [.*\.incustom, custom.InCustomFormatter]

If the file does not exist, ``musdex`` will create it implicitly during
``musdex add``. To use a config file other than the default, the
``--config`` (or ``-c``) global option can be specified prior to the
subcommand name.

.. _yaml: http://yaml.org

==========
Index File
==========

For incremental operation, ``musdex`` makes use of a non-critical index
file. This index file, created when necessary, should be hidden and
should not be kept under version control. The default location for this
index file is ``_musdex/.musdex.index.yaml``, but it can be set in the
above configuration file. Currently this index is a simple, local
mapping between files and timestamps.
