// SPDX-License-Identifier: GPL-3.0-or-later
// SPDX-FileCopyrightText: Bradley M. Bell <bradbell@seanet.com>
// SPDX-FileContributor: 2020-23 Bradley M. Bell
// ----------------------------------------------------------------------------
// BEGIN_FACTORIAL
template<class T> factorial(const T& n)
// END_FACTORIAL
{   if n == static_cast<T>(1)
      return n;
   return n * factorial(n - 1);
}
//
// BEGIN_SQUARE
template<class T> square(const T& x)
// END_SQUARE
{   return x * x;
}
// BEGIN_TANGENT
template<class T> tangent(const T& x)
// END_TANGENT
{  return sin(x) / cos(x);
}
/*
------------------------------------------------------------------------------
{xrst_begin dir_example}

Dir Command Example
###################
This example is similar to the :ref:`literal_example-name` .

factorial
*********
.. literalinclude:: {xrst_dir example/dir.cpp}
   :start-after: // BEGIN_FACTORIAL
   :end-before:  // END_FACTORIAL

square
******
.. include:: {xrst_dir example/dir.cpp}
   :start-after: // BEGIN_SQUARE
   :end-before:  // END_SQUARE

tangent
*******
.. include:: {xrst_dir example/dir.cpp}
   :start-after: // BEGIN_TANGENT
   :end-before:  // END_TANGENT
   :literal:


xrst_literal
************
The file below demonstrates the use of ``xrst_dir`` .

This Example File
*****************
{xrst_literal}

{xrst_end dir_example}
------------------------------------------------------------------------------
*/
