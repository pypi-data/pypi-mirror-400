.. _next_heading-name:

!!!!!!!!!!!!
next_heading
!!!!!!!!!!!!

.. meta::
   :keywords: next_heading,return,location,of,the,next,heading,in,a,page,prototype,data,data_index,page_file,page_name,heading_index,heading_text,underline_text

.. index:: next_heading, return, location, next, heading, in, page

.. _next_heading-title:

Return location of the next heading in a page
#############################################

.. contents::
   :local:

.. index:: prototype

.. _next_heading@Prototype:

Prototype
*********

.. literalinclude:: ../../xrst/next_heading.py
   :lines: 59-65,154-158
   :language: py

.. index:: data

.. _next_heading@data:

data
****
is the data that we are searching for a heading in. The heading text must
have at least one character and be followed by an underline of at least the
same length. The heading text may be proceeded by an overline.

.. index:: data_index

.. _next_heading@data_index:

data_index
**********
is the index in the data where the search starts. This must be zero
or directly after a newline.

.. index:: page_file

.. _next_heading@page_file:

page_file
*********
name of the file that contains the input begin command for this page.
This is only used for error reporting.

.. index:: page_name

.. _next_heading@page_name:

page_name
*********
is the name of this page.
This is only used for error reporting.

.. index:: heading_index

.. _next_heading@heading_index:

heading_index
*************
If there is an overline, this is the index in data of the beginning of the
overline. Otherwise, it is the index of the beginning of the heading text.
If 0 < heading_index, there is a newline just before heading_index; i.e.,
data[heading_index]=='\n'.  If heading_index is -1, there is no heading
in data that begins at or after data_index.

.. index:: heading_text

.. _next_heading@heading_text:

heading_text
************
if 0 <= heading_index, this is the heading text.

.. index:: underline_text

.. _next_heading@underline_text:

underline_text
**************
if 0 <= heading_index, this is the underline text.
If there is an overline present, it is the same as the underline text.
