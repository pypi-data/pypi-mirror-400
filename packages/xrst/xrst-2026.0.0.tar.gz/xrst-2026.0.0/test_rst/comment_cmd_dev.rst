.. _comment_cmd_dev-name:

!!!!!!!!!!!!!!!
comment_cmd_dev
!!!!!!!!!!!!!!!

.. meta::
   :keywords: comment_cmd_dev,remove,all,comment,commands,prototype,data_in,data_out

.. index:: comment_cmd_dev, remove, all, comment, commands

.. _comment_cmd_dev-title:

Remove all comment commands
###########################

.. contents::
   :local:

.. index:: prototype

.. _comment_cmd_dev@Prototype:

Prototype
*********

.. literalinclude:: ../../xrst/comment_command.py
   :lines: 58-59,96-98
   :language: py

.. index:: data_in

.. _comment_cmd_dev@data_in:

data_in
*******
is the data for this page.

.. index:: data_out

.. _comment_cmd_dev@data_out:

data_out
********
The return data_out is a copy of data_in except that the comment
commands have been removed.
