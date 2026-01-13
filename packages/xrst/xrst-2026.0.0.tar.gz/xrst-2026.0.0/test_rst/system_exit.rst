.. _system_exit-name:

!!!!!!!!!!!
system_exit
!!!!!!!!!!!

.. meta::
   :keywords: system_exit,form,error,message,and,exit,msg,file_name,page_name,m_obj,data,line,prototype

.. index:: system_exit, form, error, message, exit

.. _system_exit-title:

Form error message and exit
###########################

.. contents::
   :local:

.. index:: msg

.. _system_exit@msg:

msg
***
Reason for aborting xrst

.. index:: file_name

.. _system_exit@file_name:

file_name
*********
is the name of the file that contains the begin command for this page.
This is different from the current input file if we are processing
a template expansion.

.. index:: page_name

.. _system_exit@page_name:

page_name
*********
name of page that the error appeared in

.. index:: m_obj

.. _system_exit@m_obj:

m_obj
*****
The error was detected in the values returned by this match object.

.. index:: data

.. _system_exit@data:

data
****
is the data that was searched to get the match object m_obj.
If the error possibly occurred in a template expansion, you must include
the entire expansion in the data.

.. index:: line

.. _system_exit@line:

line
****
is the line number in the current input file where the error
was detected.

.. index:: prototype

.. _system_exit@Prototype:

Prototype
*********

.. literalinclude:: ../../xrst/system_exit.py
   :lines: 58-67
   :language: py
