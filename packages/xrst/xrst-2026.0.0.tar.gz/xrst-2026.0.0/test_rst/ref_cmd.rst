.. _ref_cmd-name:

!!!!!!!
ref_cmd
!!!!!!!

.. meta::
   :keywords: ref_cmd,allow,multiple,lines,in,sphinx,ref,role,syntax,purpose,new,example

.. index:: ref_cmd, allow, multiple, lines, in, sphinx, ref, role

.. _ref_cmd-title:

Allow Multiple Lines in Sphinx ref Role
#######################################

.. contents::
   :local:

.. _ref_cmd@Syntax:

Syntax
******

| ``:ref:`` ` *target* `
| ``:ref:`` ` *linking_text* ``<``  *target* ``>`` `

.. _ref_cmd@Purpose:

Purpose
*******
The xrst program allows one to place a sphinx ``ref`` role target
on multiple lines.
This makes the xrst input more readable
when the headings corresponding to the target are long; see
:ref:`heading_links-name` .

.. index:: new, lines

.. _ref_cmd@New Lines:

New Lines
*********
Newlines and spaces surrounding newlines are removed  from *target* .

.. _ref_cmd@Example:

Example
*******
:ref:`ref_example-name`
