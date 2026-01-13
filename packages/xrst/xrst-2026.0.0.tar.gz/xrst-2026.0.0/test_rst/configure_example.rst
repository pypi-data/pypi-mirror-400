.. _configure_example-name:

!!!!!!!!!!!!!!!!!
configure_example
!!!!!!!!!!!!!!!!!

.. meta::
   :keywords: configure_example,example,using,toml,configure,file,include_all,rst_prolog,latex_macro,this

.. index:: configure_example, using, toml, configure

.. _configure_example-title:

Example Using TOML Configure File
#################################

.. contents::
   :local:

.. index:: include_all

.. _configure_example@include_all:

include_all
***********

.. index:: rst_prolog

.. _configure_example@include_all@rst_prolog:

rst_prolog
==========
|tab| This line is indented using ``|tab|``
which is defined in the rst_prolog for this documentation.

.. index:: latex_macro

.. _configure_example@include_all@latex_macro:

latex_macro
===========
:math:`f : \B{R}^n \rightarrow \B{R}^m`
This line uses ``\B`` which is defined as a latex_macro.

.. index:: toml

.. _configure_example@Example TOML File:

Example TOML File
*****************

.. literalinclude:: ../../xrst.toml
   :language: toml

.. _configure_example@This Example File:

This Example File
*****************

.. literalinclude:: ../../example/configure.xrst
   :language: rst
