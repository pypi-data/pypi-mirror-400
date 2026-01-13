.. _literal_cmd_dev-name:

!!!!!!!!!!!!!!!
literal_cmd_dev
!!!!!!!!!!!!!!!

.. meta::
   :keywords: literal_cmd_dev,process,the,literal,commands,in,a,page,prototype,data_in,page_file,page_name,rst2project_dir,data_out

.. index:: literal_cmd_dev, process, literal, commands, in, page

.. _literal_cmd_dev-title:

Process the literal commands in a page
######################################

.. contents::
   :local:

.. index:: prototype

.. _literal_cmd_dev@Prototype:

Prototype
*********

.. literalinclude:: ../../xrst/literal_command.py
   :lines: 222-226,405-407
   :language: py

.. index:: data_in

.. _literal_cmd_dev@data_in:

data_in
*******
is the data for a page before the
:ref:`literal commands <literal_cmd-name>` have been removed.

.. index:: page_file

.. _literal_cmd_dev@page_file:

page_file
*********
is the name of the file that contains the begin command for this page.
This is used for error reporting and for the display file
when the display file is not included in the command and the command
is not in a template expansion.

.. index:: page_name

.. _literal_cmd_dev@page_name:

page_name
*********
is the name of the page that this data is in. This is only used
for error reporting.

.. index:: rst2project_dir

.. _literal_cmd_dev@rst2project_dir:

rst2project_dir
***************
is a relative path from the :ref:`config_file@directory@rst_directory`
to the :ref:`config_file@directory@project_directory` .

.. index:: data_out

.. _literal_cmd_dev@data_out:

data_out
********
Each xrst literal command is converted to its corresponding sphinx commands.
