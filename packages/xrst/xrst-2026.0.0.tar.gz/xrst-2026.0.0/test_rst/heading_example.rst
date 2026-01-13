.. _heading_example-name:

!!!!!!!!!!!!!!!
heading_example
!!!!!!!!!!!!!!!

.. meta::
   :keywords: heading_example,heading,and,link,example,level,one,two,another,two\_,x,links,linking,headings,using,:ref:,this,file

.. index:: heading_example, heading, link

.. _heading_example-title:

Heading and Link Example
########################
Both the page name and page title are level zero headings for a page.
Using the *page_name* label displays the page name as its linking text;
e.g. for this page both the label and linking text are::

   heading_example

The *page_name*  name followed by ``-title`` displays the page title
as its linking text;
e.g. for this page the label is ``heading_example-title``
and linking text is::

   Heading and Link Example

.. contents::
   :local:

.. index:: level, one

.. _heading_example@Level One:

Level One
*********
The label for this heading is ``heading_example@Level One``.

.. index:: level, two

.. _heading_example@Level One@Level Two:

Level Two
=========
The label for this heading is ``heading_example@Level One@Level Two``.

.. index:: another, level, one

.. _heading_example@Another Level One:

Another Level One
*****************
The label for this heading is ``heading_example@Another Level One``.

.. index:: level, two\_

.. _heading_example@Another Level One@Level Two_:

Level Two\_
===========
The label for this heading is
``heading_example@Another Level One@Level Two_``.
Note that the backslash in the heading keeps ``Two_``
from being interpreted as a link.
Also note that the backslash does not appear in the
display of the heading or in the corresponding label.

.. index:: x

.. _heading_example@Another Level One@x:

x
=
A heading can have just one character.
The label for this heading is
``heading_example@Another Level One@x``.

.. index:: links

.. _heading_example@Links:

Links
*****
These links would also work from any other page because the page name
(``heading_example`` in this case)
is included at the beginning of the target for the link:

#. :ref:`heading_example-name`
#. :ref:`heading_example-title`
#. :ref:`heading_example@Level One`
#. :ref:`heading_example@Level One@Level Two`
#. :ref:`heading_example@Another Level One`
#. :ref:`heading_example@Another Level One@Level Two_`
#. :ref:`heading_example@Another Level One@x`

.. index:: linking, headings, using, :ref:

.. _heading_example@Linking Headings Using :ref\::

Linking Headings Using :ref:
****************************
The file below demonstrates linking to headings using ``:ref:`` .

.. _heading_example@This Example File:

This Example File
*****************

.. literalinclude:: ../../example/heading.py
   :language: py
