.. _ref_example-name:

!!!!!!!!!!!
ref_example
!!!!!!!!!!!

.. meta::
   :keywords: ref_example,sphinx,ref,role,example,a,level,one,long,heading,two,three,four,links,newlines,in,:ref:,targets,this,file

.. index:: ref_example, sphinx, ref, role

.. _ref_example-title:

Sphinx ref Role Example
#######################
This example is similar to the :ref:`heading_example-name`
except that it uses multiple lines for the
targets under :ref:`ref_example@Links` below.

.. contents::
   :local:

.. index:: level, one, long, heading

.. _ref_example@A Level One Long Heading:

A Level One Long Heading
************************
Text at level one.

.. index:: level, two, long, heading

.. _ref_example@A Level One Long Heading@A Level Two Long Heading:

A Level Two Long Heading
========================
Text at level two.

.. index:: level, three, long, heading

.. _ref_example@A Level One Long Heading@A Level Two Long Heading@A Level Three Long Heading:

A Level Three Long Heading
--------------------------
Text at level three.

.. index:: level, four, long, heading

.. _ref_example@A Level One Long Heading@A Level Two Long Heading@A Level Three Long Heading@A Level Four Long Heading:

A Level Four Long Heading
.........................
Text at level four.

.. index:: links

.. _ref_example@Links:

Links
*****
The links below have newlines in their targets:

#. :ref:`level one<ref_example@A Level One Long Heading>`
#. :ref:`level two<ref_example@A Level One Long Heading@A Level Two Long Heading>`
#. :ref:`level three<ref_example@A Level One Long Heading@A Level Two Long Heading@A Level Three Long Heading>`
#. :ref:`ref_example@A Level One Long Heading@A Level Two Long Heading@A Level Three Long Heading@A Level Four Long Heading`

.. index:: newlines, in, sphinx, :ref:, targets

.. _ref_example@Newlines In Sphinx :ref\: Targets:

Newlines In Sphinx :ref: Targets
********************************
The file below demonstrates
using newlines in sphinx ``:ref:`` targets.

.. _ref_example@This Example File:

This Example File
*****************

.. literalinclude:: ../../example/ref.xrst
   :language: rst
