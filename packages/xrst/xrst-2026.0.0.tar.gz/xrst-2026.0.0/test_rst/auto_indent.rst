.. _auto_indent-name:

!!!!!!!!!!!
auto_indent
!!!!!!!!!!!

.. meta::
   :keywords: auto_indent,automatic,indentation,prototype,data,file_name,page_name

.. index:: auto_indent, automatic, indentation

.. _auto_indent-title:

Automatic Indentation
#####################
Compute the indentation at the beginning of every line in *data* .
The characters that can be used to indent are spaces or tabs.
Lines that only have spaces and tabs are not included in this calculation.

.. contents::
   :local:

.. index:: prototype

.. _auto_indent@Prototype:

Prototype
*********

.. literalinclude:: ../../xrst/auto_indent.py
   :lines: 52-55,105-106
   :language: py

.. index:: data

.. _auto_indent@data:

data
****
is the data we are computing the indentation for.
The text before the first new_line does not matter.
If you want to include this text, add a newline at the beginning of *data*.

.. index:: file_name

.. _auto_indent@file_name:

file_name
*********
used for error reporting when *data* mixes spaces and tabs in
the indentation.

.. index:: page_name

.. _auto_indent@page_name:

page_name
*********
used for error reporting when *data* mixes spaces and tabs in
the indentation.

.. index:: indentation

.. _auto_indent@indentation:

indentation
***********
The return value *indentation* is the automatically computed indentation.
It will be a sequence of spaces or tabs but it will not mix
spaces and tabs.
