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
{xrst_begin literal_example}

Literal Command Example
#######################
This example is similar to the :ref:`dir_example-name` .

Prototype
*********
{xrst_literal ,
   // BEGIN_FACTORIAL, // END_FACTORIAL
   // BEGIN_SQUARE,    // END_SQUARE
   // BEGIN_TANGENT,   // END_TANGENT
}

T
*
This is a numeric type that is used for the calculation.

factorial
*********
Returns the factorial of its argument *n* .

square
******
Returns the square of its argument *x* .

tangent
*******
Returns the tangent corresponding to its argument *x* .


xrst_literal
************
The file below demonstrates the use of ``xrst_literal`` .

This Example File
*****************
{xrst_literal}

{xrst_end literal_example}
------------------------------------------------------------------------------
*/
