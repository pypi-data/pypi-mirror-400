.. _add_line_numbers-name:

!!!!!!!!!!!!!!!!
add_line_numbers
!!!!!!!!!!!!!!!!

.. meta::
   :keywords: add_line_numbers,add,line,numbers,to,file,data,prototype,data_in,file_in,data_out

.. index:: add_line_numbers, add, line, numbers, data

.. _add_line_numbers-title:

Add Line Numbers to File Data
#############################
Add line numbers to a string in a way that is useful for reporting errors
(for modified versions of string) using line number in the original string.

.. contents::
   :local:

.. index:: prototype

.. _add_line_numbers@Prototype:

Prototype
*********

.. literalinclude:: ../../xrst/add_line_numbers.py
   :lines: 52-54,121-123
   :language: py

.. index:: data_in

.. _add_line_numbers@data_in:

data_in
*******
The original string.  An empty line is a line with just spaces or tabs.
line_number is the number of newlines before a line plus one; i.e.,
the first line is number one.

.. index:: file_in

.. _add_line_numbers@file_in:

file_in
*******
is the file corresponding to data_in (used for error reporting).

.. index:: data_out

.. _add_line_numbers@data_out:

data_out
********
The return data_out is a modified version of data_in. The text

 | ``@xrst_line`` *line_number* ``@``

is added at the end of each non-empty line.
There is one space between ``@xrst_line`` and *line_number*.
There is no space between *line_number* and ``@`` .
Spaces and tabs in empty lines are removed (so they are truly empty).
