.. _sphinx_label-name:

!!!!!!!!!!!!
sphinx_label
!!!!!!!!!!!!

.. meta::
   :keywords: sphinx_label,get,labels,declared,using,sphinx,commands,prototype,data,page_file,page_name,m_external_label,m_internal_label,errors

.. index:: sphinx_label, get, labels, declared, using, sphinx, commands

.. _sphinx_label-title:

Get Labels Declared Using Sphinx Commands
#########################################

.. contents::
   :local:

.. index:: prototype

.. _sphinx_label@Prototype:

Prototype
*********

.. literalinclude:: ../../xrst/sphinx_label.py
   :lines: 71-74,156-161
   :language: py

.. index:: data

.. _sphinx_label@data:

data
****
is the data for this page.

.. index:: page_file

.. _sphinx_label@page_file:

page_file
*********
is the name of the xrst file containing the begin command for this page
(only used for error reporting).

.. index:: page_name

.. _sphinx_label@page_name:

page_name
*********
is the page name corresponding to *data*
(only used for error reporting).

.. index:: m_external_label

.. _sphinx_label@m_external_label:

m_external_label
****************
For each label declared in *data* using sphinx commands,
and that links to an external web site,
*m_external_label* [ *label*.lower() ] is a match object
for the label in *data* .

.. index:: m_internal_label

.. _sphinx_label@m_internal_label:

m_internal_label
****************
For each label declared in *data* using sphinx commands,
and that links to a page in this web site,
*internal* [ *label* ] is a match object
for the label in *data* .

.. index:: errors

.. _sphinx_label@Errors:

Errors
******
If two external labels have the same lower case value,
an error is reported using :ref:`system_exit-name` .
