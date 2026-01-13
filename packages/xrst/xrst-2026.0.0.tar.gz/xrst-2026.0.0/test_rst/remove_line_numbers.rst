.. _remove_line_numbers-name:

!!!!!!!!!!!!!!!!!!!
remove_line_numbers
!!!!!!!!!!!!!!!!!!!

.. meta::
   :keywords: remove_line_numbers,remove,the,number,numbers,prototype,data_in,data_out,rst2xrst_list,first,tuple,element,second,third,fourth,fourthtuple

.. index:: remove_line_numbers, remove, number, numbers

.. _remove_line_numbers-title:

Remove the number numbers
#########################

.. contents::
   :local:

.. index:: prototype

.. _remove_line_numbers@Prototype:

Prototype
*********

.. literalinclude:: ../../xrst/remove_line_numbers.py
   :lines: 78-79,186-193
   :language: py

.. index:: data_in

.. _remove_line_numbers@data_in:

data_in
*******
is a string with line number markers added by :ref:`add_line_numbers-name` .
These lines number markers have the form:

    ``@xrst_line`` *line_number* ``@`` .

.. index:: data_out

.. _remove_line_numbers@data_out:

data_out
********
The return data_out is a copy of data_in with the
line number markers removed.

.. index:: rst2xrst_list

.. _remove_line_numbers@rst2xrst_list:

rst2xrst_list
*************
The second return rst2xrst_list is a list of tuples.
Each tuple in the list has two or four elements.

.. index:: first, tuple, element

.. _remove_line_numbers@rst2xrst_list@First Tuple Element:

First Tuple Element
===================
is the line number in *data_out* corresponding to a line number marker
that was removed from *data_in* .
The lines in *data_out*  still contain the ``{xrst@before_title}`` commands
that were in *data_in*.
These are not included in the line number could (because they are
removed before writing its rst file).

.. index:: second, tuple, element

.. _remove_line_numbers@rst2xrst_list@Second Tuple Element:

Second Tuple Element
====================
The second tuple element is the line number in the file that contains
the begin command for this page.

.. index:: third, tuple, element

.. _remove_line_numbers@rst2xrst_list@Third Tuple Element:

Third Tuple Element
===================
This element is present If the current line in *data_out* is
part of a template expansion.
In this case, the third element is the template file name.

.. index:: fourth, tuple, element

.. _remove_line_numbers@rst2xrst_list@Fourth Tuple Element:

Fourth Tuple Element
====================
This element is present If the current line in *data_out* is
part of a template expansion.
In this case, the fourth element is the line in the template file.

.. index:: fourthtuple, element

.. _remove_line_numbers@rst2xrst_list@FourthTuple Element:

FourthTuple Element
===================
If the current line in data_out corresponds to a template file,
this is the line number in the template file. Otherwise, it is None.
