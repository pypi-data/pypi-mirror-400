.. _replace_spell-name:

!!!!!!!!!!!!!
replace_spell
!!!!!!!!!!!!!

.. meta::
   :keywords: replace_spell,replace,spelling,commands,tmp_dir,spell.toml,prototype

.. index:: replace_spell, replace, spelling, commands

.. _replace_spell-title:

Replace spelling commands
#########################

.. contents::
   :local:

.. index:: tmp_dir

.. _replace_spell@tmp_dir:

tmp_dir
*******
is the directory where spell.toml is located

.. index:: spell.toml

.. _replace_spell@spell.toml:

spell.toml
**********
The file *tmp_dir* ``/spell.toml`` contains the information below.
For each file that was included in the documentation,
for each page in that file::

    [file_name.page_name]
    begin_line  = integer line number where begin command is located
    start_spell = integer line number where the spell command starts
    end_spell   = integer line number where the spell command ends
    replace     = array of strings (words) that are not in dictionary

It is called spell.tom because it is written by the
:ref:`spell_cmd_dev-name` one page at a time.

#.  file_name and page_name are strings.
#.  file_name is relative to the
    :ref:`config_file@directory@project_directory` .
#.  Descriptions to the left (right) of the equal signs are literal text
    (replaced by their values).
#.  Line numbers start at one and are for the specified file.
#.  The line number zero is used for start_spell and end_spell when
    there is no spell command for this page.
#.  The spell start and end lines do not overlap the begin line.

.. index:: prototype

.. _replace_spell@Prototype:

Prototype
*********

.. literalinclude:: ../../xrst/replace_spell.py
   :lines: 53-54
   :language: py
