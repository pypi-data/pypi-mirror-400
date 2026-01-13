.. _comment_ch_cmd-name:

!!!!!!!!!!!!!!
comment_ch_cmd
!!!!!!!!!!!!!!

.. meta::
   :keywords: comment_ch_cmd,comment,character,command,syntax,purpose,ch,input,stream,indentation,example

.. index:: comment_ch_cmd, comment, character

.. _comment_ch_cmd-title:

Comment Character Command
#########################

.. contents::
   :local:

.. _comment_ch_cmd@Syntax:

Syntax
******
``{xrst_comment_ch`` *ch* ``}``

.. _comment_ch_cmd@Purpose:

Purpose
*******
Some languages have a special character that
indicates the rest of the line is a comment.
If you embed sphinx documentation in this type of comment,
you need to inform xrst of the special character so it does
not end up in your ``.rst`` output file.

.. index:: ch

.. _comment_ch_cmd@ch:

ch
**
The value of *ch* must be one non white space character.
There must be at least one white space character
between ``xrst_comment_ch`` and *ch*.
Leading and trailing white space around *ch* is ignored.

.. index:: input, stream

.. _comment_ch_cmd@Input Stream:

Input Stream
************
Spaces and tabs before the special character,
the special character,
and one space directory after the special character (if present),
are removed from the input stream before any xrst processing.
For example, if :code:`#` is the special character,
the following input has the heading Factorial
and the ``def`` token indented the same amount:

.. code-block:: py

   # Factorial
   # ---------
   def factorial(n) :
      if n == 1 :
         return 1
      return n * factorial(n-1)

.. index:: indentation

.. _comment_ch_cmd@Indentation:

Indentation
***********
The :ref:`indent commands<indent_cmd-name>`
are processed before removing the special character and its white space.

.. _comment_ch_cmd@Example:

Example
*******
:ref:`comment_ch_example-name`
