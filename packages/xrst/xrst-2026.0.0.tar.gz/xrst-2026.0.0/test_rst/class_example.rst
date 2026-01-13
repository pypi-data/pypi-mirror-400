.. _class_example-name:

!!!!!!!!!!!!!
class_example
!!!!!!!!!!!!!

.. meta::
   :keywords: class_example,example,documenting,a,class,syntax,prototype,discussion,test,this,file

.. index:: class_example, documenting, class

.. _class_example-title:

Example Documenting a Class
###########################

.. contents::
   :local:

.. _class_example@Syntax:

Syntax
******
| |tab| ``ad_double`` *var* ( *value* , *derivative* )
| |tab| ``ad_double`` *other* ( *value* , *derivative* )
| |tab| *var*.\ ``value``\ ()
| |tab| *var*.\ ``derivative``\ ()
| |tab| *var* + *other*
| |tab| *var* - *other*
| |tab| *var* * *other*
| |tab| *var* / *other*

.. index:: prototype

.. _class_example@Prototype:

Prototype
*********

.. literalinclude:: ../../example/class.cpp
   :lines: 74-74,79-79,84-84,89-89,97-97,105-105,114-114
   :language: cpp

.. index:: discussion

.. _class_example@Discussion:

Discussion
**********
The class ``ad_double`` implements forward mode Algorithm Differentiation (AD)
for the add, subtract, multiply and divide operations.

.. _class_example@Example:

Example
*******
The function :ref:`example_ad_double-name` is an example for using this class.

.. index:: test

.. _class_example@Test:

Test
****
The main program :ref:`test_ad_double-name` runs the example above.

.. _class_example@This Example File:

This Example File
*****************

.. literalinclude:: ../../example/class.cpp
   :language: cpp

.. toctree::
   :maxdepth: 1
   :hidden:

   example_ad_double
   test_ad_double
