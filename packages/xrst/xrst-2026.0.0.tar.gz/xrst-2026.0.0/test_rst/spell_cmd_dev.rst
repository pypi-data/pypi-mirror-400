.. _spell_cmd_dev-name:

!!!!!!!!!!!!!
spell_cmd_dev
!!!!!!!!!!!!!

.. meta::
   :keywords: spell_cmd_dev,process,the,spell,command,for,a,page,prototype,tmp_dir,data_in,page_file,page_name,begin_line,ignore_commands,print_warning,spell_checker,data_out,spell_warning,unknown_word_set

.. index:: spell_cmd_dev, process, spell, page

.. _spell_cmd_dev-title:

Process the spell command for a page
####################################

.. contents::
   :local:

.. index:: prototype

.. _spell_cmd_dev@Prototype:

Prototype
*********

.. literalinclude:: ../../xrst/spell_command.py
   :lines: 239-254,610-614
   :language: py

.. index:: tmp_dir

.. _spell_cmd_dev@tmp_dir:

tmp_dir
*******
The file :ref:`replace_spell@spell.toml`
is written in the *tmp_dir* directory by the one page at a time
by this function call.

.. index:: data_in

.. _spell_cmd_dev@data_in:

data_in
*******
is the data for this page before the spell commands are removed.

.. index:: page_file

.. _spell_cmd_dev@page_file:

page_file
*********
is the name of the file where the begin command for this page appears.
This is used for error reporting and for creating spell.toml.

.. index:: page_name

.. _spell_cmd_dev@page_name:

page_name
*********
is the name of the page that this data is in. This is only used
for error reporting and spell.toml.

.. index:: begin_line

.. _spell_cmd_dev@begin_line:

begin_line
**********
is the line number in *page_file* where the begin command for this page
appears. This is only used for spell.toml.

.. index:: ignore_commands

.. _spell_cmd_dev@ignore_commands:

ignore_commands
***************
If this is true (false), :ref:`run_xrst@ignore_spell_commands`
was (was not) on the command line.

.. index:: print_warning

.. _spell_cmd_dev@print_warning:

print_warning
*************
if this is false, do not print the spelling warnings. Otherwise,
a spelling warning is reported for each word (and double word) that is not
in the spell_checker dictionary or the special word list. A word is two or
more letter characters. If a word is directly preceded by a backslash,
it is ignored (so that latex commands do not generate warnings).

.. index:: spell_checker

.. _spell_cmd_dev@spell_checker:

spell_checker
*************
Is a spell checking object used for error checking; see
:ref:`get_spell_checker-name`.

.. index:: data_out

.. _spell_cmd_dev@data_out:

data_out
********
is the data for this page after the spell command (if it exists)
is removed.

.. index:: spell_warning

.. _spell_cmd_dev@spell_warning:

spell_warning
*************
is true if a spelling error occurred and a warning was printed.
Otherwise, it is false.

.. index:: unknown_word_set

.. _spell_cmd_dev@unknown_word_set:

unknown_word_set
****************
is a lower case version of the set of words that are not in the
spell_checker dictionary or the special word list.
It does not include double word errors.
