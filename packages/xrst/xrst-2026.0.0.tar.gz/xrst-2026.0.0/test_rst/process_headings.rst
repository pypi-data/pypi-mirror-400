.. _process_headings-name:

!!!!!!!!!!!!!!!!
process_headings
!!!!!!!!!!!!!!!!

.. meta::
   :keywords: process_headings,add,labels,and,index,entries,for,headings,prototype,check_headings,conf_dict,local_toc,data_in,page_file,page_name,not_in_index_list,data_out,page_title,pseudo_heading,keywords

.. index:: process_headings, add, labels, index, entries, headings

.. _process_headings-title:

Add labels and index entries for headings
#########################################

.. contents::
   :local:

.. index:: prototype

.. _process_headings@Prototype:

Prototype
*********

.. literalinclude:: ../../xrst/process_headings.py
   :lines: 274-289,600-607
   :language: py

.. index:: check_headings

.. _process_headings@check_headings:

check_headings
**************
If *check* is true, an error in a headings or its corresponding label,
will result in an error message and program exit.
This should be True on the first call and false on the second.
Two passes are required because *data_out* does not change on the
first pass so that all the match objects can be used for error messaging.

.. index:: conf_dict

.. _process_headings@conf_dict:

conf_dict
*********
is a python dictionary representation of the configuration file.

.. index:: local_toc

.. _process_headings@local_toc:

local_toc
*********
is the xrst command line local_toc setting.

.. index:: data_in

.. _process_headings@data_in:

data_in
*******
contains the data for a page before the headings are processed.

.. index:: page_file

.. _process_headings@page_file:

page_file
*********
name of the file that contains the begin command for this page.
This is only used for error reporting.

.. index:: page_name

.. _process_headings@page_name:

page_name
*********
is the name of this page.

.. index:: not_in_index_list

.. _process_headings@not_in_index_list:

not_in_index_list
*****************
is a list of compiled regular expressions. If pattern is in this list,
*word* is a lower case version of a word in the heading text, and
pattern.fullmatch( *word* ) returns a match, an index entry is not
generated for word.

.. index:: data_out

.. _process_headings@data_out:

data_out
********
is a copy of data_in with the following extra command added:

 #. The index entries, and meta keyword entries (same as index),
    and the :ref:`heading_links@Labels` for this page.
 #. The command \\n{xrst@before_title} is placed directly before the
    first heading for this page; i.e. its title.
    This is makes it easy to add the page number to the heading text.

.. index:: page_title

.. _process_headings@page_title:

page_title
**********
This is the heading text in the first heading for this page.
There can only be one heading at this level.

.. index:: pseudo_heading

.. _process_headings@pseudo_heading:

pseudo_heading
**************
This is an automatically generated heading for this page. It is intended
to come before the page_title heading.
It has three lines each terminated by a newline:

 1. an overline line
 2. heading text line for this page title
 3. an underline line

.. index:: keywords

.. _process_headings@keywords:

keywords
********
This is a space separated  list, of the lower case words,
for all the words that are in the # title and the headings for this page.
This is the same as the index words for this page minus the words that
match *not_in_index_list* .
