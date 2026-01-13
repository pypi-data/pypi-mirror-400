.. _indent_cmd-name:

!!!!!!!!!!
indent_cmd
!!!!!!!!!!

.. meta::
   :keywords: indent_cmd,indent,command,syntax,discussion,indentation,automatic,comment,character,example

.. index:: indent_cmd, indent

.. _indent_cmd-title:

Indent Command
##############

.. contents::
   :local:

.. _indent_cmd@Syntax:

Syntax
******
*indentation* ``{xrst_indent}``

.. index:: discussion

.. _indent_cmd@Discussion:

Discussion
**********
#. The xrst documentation for a page can be indented so that it is grouped
   with the source code it is next to.
#. We call lines that have just spaces or tabs empty lines
#. Empty lines below an indent command, and before the next indent command,
   must begin with *indent* . The indent characters
   are not included in the rst output; i.e., the indentation is removed.
#. If there is an indent command in a page,
   lines before the first indent command do not have any indentation.
#. If there is no indent command in a page,
   the indentation for the page is computed automatically.

.. index:: indentation

.. _indent_cmd@indentation:

indentation
***********
This is the sequence of spaces or a sequence of tabs that
come before ``{xrst_indent}`` .
It cannot mix both spaces and tabs.

.. index:: automatic, indentation

.. _indent_cmd@Automatic Indentation:

Automatic Indentation
*********************
If there is no indent command in a page,
the indentation is calculated automatically as follows:
The number of spaces (or tabs) before
all of the xrst documentation for a page
(not counting lines with just spaces or tabs)
is used for the indentation for that page.

.. index:: comment, character

.. _indent_cmd@Comment Character:

Comment Character
*****************
The indentation is calculated before processing the
:ref:`comment_ch_cmd-name` command.

.. _indent_cmd@Example:

Example
*******
:ref:`indent_example-name`,
:ref:`comment_ch_example@Indent`, and
:ref:`example_ad_double@xrst_indent` .
