.. _check_input_files-name:

!!!!!!!!!!!!!!!!!
check_input_files
!!!!!!!!!!!!!!!!!

.. meta::
   :keywords: check_input_files,check,that,expected,xrst,input,files,are,included,prototype,config_file,conf_dict,group_name,toc_file_set,file_list_in,file_list_out,file_list_warning

.. index:: check_input_files, check, expected, xrst, input, files, are, included

.. _check_input_files-title:

Check That Expected xrst Input Files Are Included
#################################################

.. contents::
   :local:

.. index:: prototype

.. _check_input_files@Prototype:

Prototype
*********

.. literalinclude:: ../../xrst/check_input_files.py
   :lines: 63-77,187-192
   :language: py

.. index:: config_file

.. _check_input_files@config_file:

config_file
***********
is the name of the configuration file.

.. index:: conf_dict

.. _check_input_files@conf_dict:

conf_dict
*********
is a python dictionary representation of the configuration file.

.. index:: group_name

.. _check_input_files@group_name:

group_name
**********
is the name of the group that we are checking

.. index:: toc_file_set

.. _check_input_files@toc_file_set:

toc_file_set
************
is the set of files that were included by toc commands starting
at the root file for this group.
A warning is printed if a file has a begin command for this group
and it is not in *toc_file_set*.

.. index:: file_list_in

.. _check_input_files@file_list_in:

file_list_in
************
If file_list_in is None, the :ref:`config_file@input_files` commands
will be executed to determine the file list.
Otherwise, *file_list_in* will be used as the output of the first
successful command.

.. index:: file_list_out

.. _check_input_files@file_list_out:

file_list_out
*************
This is a value that can be used for *file_list_in* to avoid
having to re-execute the input_files commands.

.. index:: file_list_warning

.. _check_input_files@file_list_warning:

file_list_warning
*****************
This is true (false) if an input file list warning is (is not) printed
