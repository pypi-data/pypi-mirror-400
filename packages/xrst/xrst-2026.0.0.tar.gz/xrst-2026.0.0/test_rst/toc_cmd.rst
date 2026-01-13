.. _toc_cmd-name:

!!!!!!!
toc_cmd
!!!!!!!

.. meta::
   :keywords: toc_cmd,table,of,children,commands,syntax,toc_hidden,toc_list,toc_table,contents,order,file,list,empty,child,links,toctree,example

.. index:: toc_cmd, table, children, commands

.. _toc_cmd-title:

Table of Children Commands
##########################

.. contents::
   :local:

.. _toc_cmd@Syntax:

Syntax
******

.. index:: toc_hidden

.. _toc_cmd@Syntax@toc_hidden:

toc_hidden
==========
| ``{xrst_toc_hidden`` *order*
|   *file_1*
|   ...
|   *file_n*
| ``}``

.. index:: toc_list

.. _toc_cmd@Syntax@toc_list:

toc_list
========
| ``{xrst_toc_list`` *order*
|   *file_1*
|   ...
|   *file_n*
| ``}``

.. index:: toc_table

.. _toc_cmd@Syntax@toc_table:

toc_table
=========
| ``{xrst_toc_table`` *order*
|   *file_1*
|   ...
|   *file_n*
| ``}``

.. index:: table, contents

.. _toc_cmd@Table of Contents:

Table of Contents
*****************
These commands specify the pages that are children
of the current page; i.e., pages that are at the
next level in the table of contents.
They also specify the form for the table of contents
and where it appears.

.. index:: order

.. _toc_cmd@order:

order
*****
The *order* argument is optional.
It can only be present when this page begins with a
:ref:`parent begin<begin_cmd@Parent Page>` command.
If it is present it must be ``before`` or ``after`` .
It specifies if the child pages in the toc command should come
before or after the child pages in the current input file.
If *order* is not present and this is a parent page,
the default value ``before`` is used for *order* .

.. index:: list

.. _toc_cmd@File List:

File List
*********
A new line character must precede and follow each
of the file names *file_1* ... *file_n*.
Leading and trailing white space is not included in the names
The file names are  relative to the
:ref:`config_file@directory@project_directory` .
This may seem verbose, but it makes it easier to write scripts
that move files and automatically change references to them.

.. index:: empty

.. _toc_cmd@File List@Empty:

Empty
=====
If there are no files specified in the command,
this page must start with a
:ref:`parent begin<begin_cmd@Parent Page>` command.
(Otherwise, this page would have no children and there would be no
purpose to the command.)

.. index:: children

.. _toc_cmd@Children:

Children
********
Each of the files may contain multiple :ref:`pages<begin_cmd@Page>`.
The first of these pages may use a
:ref:`parent begin<begin_cmd@Parent Page>` command.

#. The first page in a file is always a child of the
   page where the toc command appears..

#. If the first page in a file is a begin parent page,
   the other pages in the file are children of the first page.
   Hence the other pages are grand children of the page
   where the begin toc command appears.

#. If there is no begin parent command in a file,
   all the pages in the file are children of the
   page where the toc command appears.

#. If the first page in a file is a begin parent page,
   there is also a toc command in this page,
   and *order* is ``before`` ( ``after`` )
   links to the toc command children come before (after) links to
   the children that are other pages in the same file.

.. index:: child, links

.. _toc_cmd@Child Links:

Child Links
***********
#. The toc_list syntax generates links to the children that
   display the title for each page.
   The toc_table syntax generates links to the children that
   display both the page name and page tile.

#. If a page has a toc_list or toc_table command,
   links to all the children of the page are placed where the
   toc command is located.
   You can place a heading directly before these commands
   to make the links easier to find.

#. If a page uses the hidden syntax,
   no automatic links to the children of the current page are generated.

#. If a page does not have a toc command,
   and it has a begin parent command,
   links to the children of the page are placed at the end of the page.

.. index:: toctree

.. _toc_cmd@toctree:

toctree
*******
These commands replaces the sphinx ``toctree`` directive.
A ``toctree`` directive is automatically generated and includes each
page that is a child of the current page.

.. _toc_cmd@Example:

Example
*******
:ref:`toc_list_example-name`
