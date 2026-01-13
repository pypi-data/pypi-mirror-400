.. _suspend_cmd-name:

!!!!!!!!!!!
suspend_cmd
!!!!!!!!!!!

.. meta::
   :keywords: suspend_cmd,suspend,and,resume,commands,syntax,discussion,white,space,boolean,*op*,left,,right,example

.. index:: suspend_cmd, suspend, resume, commands

.. _suspend_cmd-title:

Suspend and Resume Commands
###########################

.. contents::
   :local:

.. _suspend_cmd@Syntax:

Syntax
******
- ``{xrst_suspend}``
- ``{xrst_suspend`` *boolean* ``}``
- ``{xrst_suspend`` *left* *op* *right* ``}``
- ``{xrst_resume}``

.. index:: discussion

.. _suspend_cmd@Discussion:

Discussion
**********
It is possible to suspend (resume) the xrst extraction and processing.
One begins (ends) the suspension with a line that only contains spaces,
tabs and a suspend command (resume command).
Each suspend command must have a corresponding resume command.

.. index:: white, space

.. _suspend_cmd@White Space:

White Space
***********
Leading and trailing spaces in *boolean* , *left* , *op* , and *right*
are ignored.

.. index:: boolean

.. _suspend_cmd@boolean:

boolean
*******
If the argument *boolean* is present, it must be true or false.
If is true, or not present, the section of input up to the next resume
is not included in the xrst extraction and processing for this page.
This argument is intended to be used by the
template command where it can be assigned the value true or false
for a particular expansion of the :ref:`template_cmd@template_file` .

.. index:: *op*

.. _suspend_cmd@*op*:

*op*
****
This argument must be ``==`` or ``!=``.
It must be separated one or more spaces from *left* and *right* .

.. index:: left,, right

.. _suspend_cmd@left, right:

left, right
***********
If arguments *left* and *right* must not have any white space in them.
If

 *left* *op* *right*

is true (false) ,
the section of input up to the next resume
is not included in the xrst extraction and processing for this page.

.. _suspend_cmd@Example:

Example
*******
:ref:`suspend_example-name`
