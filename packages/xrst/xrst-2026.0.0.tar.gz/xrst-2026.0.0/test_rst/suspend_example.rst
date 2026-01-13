.. _suspend_example-name:

!!!!!!!!!!!!!!!
suspend_example
!!!!!!!!!!!!!!!

.. meta::
   :keywords: suspend_example,suspend,command,example,discussion,project_name,xrst_code,xrst_suspend,this,file

.. index:: suspend_example, suspend

.. _suspend_example-title:

Suspend Command Example
#######################

.. contents::
   :local:

.. index:: discussion

.. _suspend_example@Discussion:

Discussion
**********
The project_name paragraph below
was taken from the xrst configure file documentation.

#. The documentation for the default table uses toml file format.
#. The python code that implements this default comes directly after
   and is not displayed in the documentation.

.. index:: project_name

.. _suspend_example@project_name:

project_name
************
The only value in this table is the name of this project.
The default for this table is

.. literalinclude:: ../../example/suspend.py
   :lines: 27-28
   :language: toml

.. index:: xrst_code

.. _suspend_example@xrst_code:

xrst_code
*********
The file below uses ``xrst_code`` to display the toml version
of this default setting.

.. index:: xrst_suspend

.. _suspend_example@xrst_suspend:

xrst_suspend
************
The file below uses ``xrst_suspend`` to avoid displaying the python version
of this default setting.

.. _suspend_example@This Example File:

This Example File
*****************

.. literalinclude:: ../../example/suspend.py
   :language: py
