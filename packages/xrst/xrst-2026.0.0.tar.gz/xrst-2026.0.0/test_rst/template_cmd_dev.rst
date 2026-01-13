.. _template_cmd_dev-name:

!!!!!!!!!!!!!!!!
template_cmd_dev
!!!!!!!!!!!!!!!!

.. meta::
   :keywords: template_cmd_dev,expand,the,template,commands,in,a,page,prototype,restrictions,data_in,page_file,page_name,data_out

.. index:: template_cmd_dev, expand, template, commands, in, page

.. _template_cmd_dev-title:

Expand the template commands in a page
######################################

.. contents::
   :local:

.. index:: prototype

.. _template_cmd_dev@Prototype:

Prototype
*********

.. literalinclude:: ../../xrst/template_command.py
   :lines: 189-192,380-381
   :language: py

.. index:: restrictions

.. _template_cmd_dev@Restrictions:

Restrictions
************
The template expansion must come before processing any other commands
except for the following:
begin, end, comment_ch, indent, suspend, resume, spell, template.

.. index:: data_in

.. _template_cmd_dev@data_in:

data_in
*******
is the data for a page before the
:ref:`template commands <template_cmd-name>` have been expanded.

.. index:: page_file

.. _template_cmd_dev@page_file:

page_file
*********
is the name of the file, for this page, where the begin command appears.
This is used for error reporting .

.. index:: page_name

.. _template_cmd_dev@page_name:

page_name
*********
is the name of the page that this data is in. This is only used
for error reporting.

.. index:: data_out

.. _template_cmd_dev@data_out:

data_out
********
Each xrst template command is expanded and
xrst.add_line_numbers is used to add line numbers corresponding to the
template file.
In addition, the following text is added at the beginning and end of the
expansion:

| |tab| @ ``{xrst_template_begin`` @ *template_file* @ *page_line* @ ``}`` @
| |tab| @ ``{xrst_template_end}`` @

where *page_line* is the line where the line number in *page_file*
where the template command appeared. There is no white space between
the tokens above.
