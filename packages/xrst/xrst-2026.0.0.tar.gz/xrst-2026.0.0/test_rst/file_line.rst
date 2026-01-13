.. _file_line-name:

!!!!!!!!!
file_line
!!!!!!!!!

.. meta::
   :keywords: file_line,determine,input,file,and,line,m_obj,data,page_file,page_line,template_file,template_line

.. index:: file_line, determine, input, line

.. _file_line-title:

Determine Input File and Line
#############################

.. literalinclude:: ../../xrst/file_line.py
   :lines: 56-58,86-93
   :language: py

.. contents::
   :local:

.. index:: m_obj

.. _file_line@m_obj:

m_obj
*****
is a match object for a location in data.

.. index:: data

.. _file_line@data:

data
****
is the data for a page including template commands (or expansions
if the templates commands have been processed).

.. index:: page_file

.. _file_line@page_file:

page_file
*********
This is the file where the begin and end commands appear for this page.

.. index:: page_line

.. _file_line@page_line:

page_line
*********
is the line number in the *page_file* corresponding to *m_obj*  .
If *template_file* is None, *m_obj* starts at this line.
Otherwise the template expansion for *template_file* starts at this line.

.. index:: template_file

.. _file_line@template_file:

template_file
*************
is the name of the file for the template expansion where the start of
*m_obj* is located.  If *m_obj* does not start in a template expansion,
*template_file* is None.
In this case, *m_obj* starts in the file where the begin command for this
page is located.

.. index:: template_line

.. _file_line@template_line:

template_line
*************
if *template_file* is None, *template_line* is None.
Otherwise it is the line number in the *template_file* for this
corresponding to this expansion.
