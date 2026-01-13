.. _get_file_info-name:

!!!!!!!!!!!!!
get_file_info
!!!!!!!!!!!!!

.. meta::
   :keywords: get_file_info,get,information,for,all,pages,in,a,file,prototype,all_page_info,group_name,parent_file,file_in,file_page_info,info['page_name'],info['page_data'],info['is_parent'],info['is_child'],info['begin_line'],info['end_line']

.. index:: get_file_info, get, information, all, pages, in

.. _get_file_info-title:

Get information for all pages in a file
#######################################

.. contents::
   :local:

.. index:: prototype

.. _get_file_info@Prototype:

Prototype
*********

.. literalinclude:: ../../xrst/get_file_info.py
   :lines: 188-200,414-417
   :language: py

.. index:: all_page_info

.. _get_file_info@all_page_info:

all_page_info
*************
a list of with information for pages that came before this file.
For each list index, all_page_info[index] is a dict and
all_page_info[index]['page_name'] is an str
containing the name of a page that came before this file.
This includes pages for all the groups that came before this group.

.. index:: group_name

.. _get_file_info@group_name:

group_name
**********
We are only retrieving information for pages in this group.
(This is non-empty because default is used for the empty group name.)

.. index:: parent_file

.. _get_file_info@parent_file:

parent_file
***********
name of the file that included file_in.

.. index:: file_in

.. _get_file_info@file_in:

file_in
*******
is the name of the file we are getting all the information for.

.. index:: file_page_info

.. _get_file_info@file_page_info:

file_page_info
**************
The value file_page_info is a list of dict.
Each dict contains the information
for one page in this file. We use info below for one element of the list:

.. index:: info['page_name']

.. _get_file_info@file_page_info@info['page_name']:

info['page_name']
=================
is an str containing the name of a page in this file.

.. index:: info['page_data']

.. _get_file_info@file_page_info@info['page_data']:

info['page_data']
=================
is an str containing the data for this page.
This data has been processed in the following way and order.

 #. Line numbers have been added using :ref:`add_line_numbers-name` .
    This is the first operation done on a page and other operations
    assume that line numbers are present. They are removed near the end
    when the temporary file corresponding to a page is created.
 #. The page data has been restricted to the text between
    the end of the begin command and the start of the end command.
 #. The suspend / resume commands and data between such pairs
    have been removed; see :ref:`suspend_cmd-name` .
 #. The indentations for this page have been removed; see
    :ref:`indent_cmd-name` .
 #. If a comment character command is present for this page,
    the command is remove and for each line, the possible
    comment character and possible space after have been removed.

.. index:: info['is_parent']

.. _get_file_info@file_page_info@info['is_parent']:

info['is_parent']
=================
is true (false) if this is (is not) the parent page for the other
pages in this file. The parent page must be the first for this group,
and hence have index zero in file_info. In addition,
if there is a parent page, there must be at least one other page;
i.e., len(file_info) >= 2.

.. index:: info['is_child']

.. _get_file_info@file_page_info@info['is_child']:

info['is_child']
================
is true (false) if this is (is not) a child of the first page in
this file.

.. index:: info['begin_line']

.. _get_file_info@file_page_info@info['begin_line']:

info['begin_line']
==================
is the line number in *file_in* where this page begins; i.e.,
the line number where the begin command is located.

.. index:: info['end_line']

.. _get_file_info@file_page_info@info['end_line']:

info['end_line']
================
is the line number in *file_in* where this page ends; i.e.,
the line number where the end command is located.
