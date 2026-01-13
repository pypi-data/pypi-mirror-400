.. _dir_cmd-name:

!!!!!!!
dir_cmd
!!!!!!!

.. meta::
   :keywords: dir_cmd,converting,sphinx,command,file,names,syntax,purpose,file_name,example

.. index:: dir_cmd, converting, sphinx, names

.. _dir_cmd-title:

Converting Sphinx Command File Names
####################################

.. contents::
   :local:

.. _dir_cmd@Syntax:

Syntax
******
``{xrst_dir`` *file_name* ``}``

.. _dir_cmd@Purpose:

Purpose
*******
Sphinx commands that use file names must specify the file
relative to the :ref:`config_file@directory@rst_directory` .
The xrst dir command converts a file name relative to the
:ref:`config_file@directory@project_directory` to be relative to the
:ref:`config_file@directory@rst_directory` .

.. index:: file_name

.. _dir_cmd@file_name:

file_name
*********
Is a file name relative to the project directory.
The entire command gets replaced by a name for the same file
relative to the rst directory.
Leading and trailing white space in *file_name* is ignored.

.. _dir_cmd@Example:

Example
*******
:ref:`dir_example-name`
