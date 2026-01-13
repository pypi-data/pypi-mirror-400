# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: Bradley M. Bell <bradbell@seanet.com>
# SPDX-FileContributor: 2020-24 Bradley M. Bell
# ----------------------------------------------------------------------------
def factorial(n) :
   r"""
   {xrst_begin indent_example}

   Indent Example
   ##############

   Discussion
   **********
   The file below demonstrates a single indentation for an entire xrst page.
   (See :ref:`example_ad_double@xrst_indent` for an example
   that has different indentation for different parts of a page.)
   Note that underling headings works even though it is indented.

   Python Docstring
   ****************
   This example input is a python docstring for the factorial function
   defined in this file, but it is documenting indentation instead
   of the function. See :ref:`docstring_example-name` for an alternative
   way to construct a docstring.

   This Example File
   *****************
   {xrst_literal}

   {xrst_end indent_example}
   """
   if n == 1 :
      return 1
   return n * factorial(n-1)
