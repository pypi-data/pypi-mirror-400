.. _template_example-name:

!!!!!!!!!!!!!!!!
template_example
!!!!!!!!!!!!!!!!

.. meta::
   :keywords: template_example,template,command,example,xrst_template,this,file

.. index:: template_example, template

.. _template_example-title:

Template Command Example
########################

.. contents::
   :local:

.. index:: xrst_template

.. _template_example@xrst_template:

xrst_template
*************
The file below demonstrates the use of ``xrst_template`` .

.. _template_example@This Example File:

This Example File
*****************

.. literalinclude:: ../../example/template.xrst
   :language: rst

.. csv-table::
   :header: "Child", "Title"
   :widths: 20, 80

   "example_expansion_one", :ref:`example_expansion_one-title`
   "example_expansion_two", :ref:`example_expansion_two-title`

.. toctree::
   :maxdepth: 1
   :hidden:

   example_expansion_one
   example_expansion_two
