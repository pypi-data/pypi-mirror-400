.. _comment_example-name:

!!!!!!!!!!!!!!!
comment_example
!!!!!!!!!!!!!!!

.. meta::
   :keywords: comment_example,comment,command,example,xrst,comments,rst,factorial,xrst_comment,this,file

.. index:: comment_example, comment

.. _comment_example-title:

Comment Command Example
#######################

.. contents::
   :local:

.. index:: xrst, comments

.. _comment_example@xrst Comments:

xrst Comments
*************
This sentence has an inline xrst comment .
This sentence has a multiple line xrst comment directly after it.
The multiple line xrst comment is directly before this sentence.

.. index:: rst, comments

.. _comment_example@rst Comments:

rst Comments
************
This sentence has a multiple line rst comment directly after it.

.. comment:
    This rst comment spans multiple lines

The multiple line rst comment is directly before this sentence.

.. index:: factorial

.. _comment_example@Factorial:

Factorial
*********

.. literalinclude:: ../../example/comment.r
   :lines: 33-38
   :language: r

.. index:: xrst_comment

.. _comment_example@xrst_comment:

xrst_comment
************
The file below demonstrates the use of ``xrst_comment`` .

.. _comment_example@This Example File:

This Example File
*****************

.. literalinclude:: ../../example/comment.r
   :language: r
