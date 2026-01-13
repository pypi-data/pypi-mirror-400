.. _indent_cmd_dev-name:

!!!!!!!!!!!!!!
indent_cmd_dev
!!!!!!!!!!!!!!

.. meta::
   :keywords: indent_cmd_dev,process,indent,commands,in,a,page,prototype,data_in,file_name,page_name,data_out

.. index:: indent_cmd_dev, process, indent, commands, in, page

.. _indent_cmd_dev-title:

Process indent commands in a page
#################################

.. contents::
   :local:

.. index:: prototype

.. _indent_cmd_dev@Prototype:

Prototype
*********

.. literalinclude:: ../../xrst/indent_command.py
   :lines: 105-108,196-198
   :language: py

.. index:: data_in

.. _indent_cmd_dev@data_in:

data_in
*******
is the data for this page.

.. index:: file_name

.. _indent_cmd_dev@file_name:

file_name
*********
is the input that this page appears in (used for error reporting).

.. index:: page_name

.. _indent_cmd_dev@page_name:

page_name
*********
is the name of this page (used for error reporting).

.. index:: data_out

.. _indent_cmd_dev@data_out:

data_out
********
is a copy of data_in with the indentation for this section removed.
