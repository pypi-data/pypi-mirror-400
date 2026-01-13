.. _comment_ch_example-name:

!!!!!!!!!!!!!!!!!!
comment_ch_example
!!!!!!!!!!!!!!!!!!

.. meta::
   :keywords: comment_ch_example,comment,character,command,example,discussion,xrst_code,indent,xrst_comment_ch,this,file

.. index:: comment_ch_example, comment, character

.. _comment_ch_example-title:

Comment Character Command Example
#################################

.. contents::
   :local:

.. index:: discussion

.. _comment_ch_example@Discussion:

Discussion
**********
The comment character at the beginning of a line,
and one space, if a space exists directly after it the comment character,
are removed before processing xrst commands.
For this example, the comment character is ``%`` .

.. index:: xrst_code

.. _comment_ch_example@xrst_code:

xrst_code
*********
The xrst_code command reports the original source code, before removing
the comment character or the indentation.

.. literalinclude:: ../../example/comment_ch.m
   :lines: 27-34
   :language: matlab

.. index:: indent

.. _comment_ch_example@Indent:

Indent
******
Note that the special character ``%`` has the same indentation as
the source code in this page.

.. index:: xrst_comment_ch

.. _comment_ch_example@xrst_comment_ch:

xrst_comment_ch
***************
The file below demonstrates the use of ``xrst_comment_ch`` .

.. _comment_ch_example@This Example File:

This Example File
*****************

.. literalinclude:: ../../example/comment_ch.m
   :language: matlab
