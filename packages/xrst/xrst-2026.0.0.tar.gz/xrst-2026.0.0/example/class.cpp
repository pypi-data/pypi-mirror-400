// SPDX-License-Identifier: GPL-3.0-or-later
// SPDX-FileCopyrightText: Bradley M. Bell <bradbell@seanet.com>
// SPDX-FileContributor: 2020-25 Bradley M. Bell
/*
-----------------------------------------------------------------------------
{xrst_begin_parent class_example}
{xrst_spell
   var
}

Example Documenting a Class
###########################

{xrst_comment
   |tab| is defined as part of rst_prolog in xrst.toml for this project
}
Syntax
******
| |tab| ``ad_double`` *var* ( *value* , *derivative* )
| |tab| ``ad_double`` *other* ( *value* , *derivative* )
| |tab| *var*.\ ``value``\ ()
| |tab| *var*.\ ``derivative``\ ()
| |tab| *var* + *other*
| |tab| *var* - *other*
| |tab| *var* * *other*
| |tab| *var* / *other*

Prototype
*********
{xrst_literal ,
   // BEGIN_CTOR, END_CTOR
   // BEGIN_VALUE, END_VALUE
   // BEGIN_DERIVATIVE, END_DERIVATIVE
   // BEGIN_ADD, END_ADD
   // BEGIN_SUB, END_SUB
   // BEGIN_MUL, END_MUL
   // BEGIN_DIV, END_DIV
}

Discussion
**********
The class ``ad_double`` implements forward mode Algorithm Differentiation (AD)
for the add, subtract, multiply and divide operations.


Example
*******
The function :ref:`example_ad_double-name` is an example for using this class.

Test
****
The main program :ref:`test_ad_double-name` runs the example above.

{xrst_comment
   Hide the table of contents for the children of this page
   because they are discussed under Example and Test above
}
{xrst_toc_hidden }

This Example File
*****************
{xrst_literal}

{xrst_end class_example}
*/
# include <iostream>

class ad_double {
private:
   const double value_;
   const double derivative_;
public:
   // BEGIN_CTOR
   ad_double(double value, double derivative)
   // END_CTOR
   : value_(value), derivative_(derivative)
   { }
   // BEGIN_VALUE
   double value(void) const
   // END_VALUE
   {  return value_; }
   //
   // BEGIN_DERIVATIVE
   double derivative(void) const
   // END_DERIVATIVE
   {  return derivative_; }
   //
   // BEGIN_ADD
   ad_double operator+(const ad_double& other) const
   // END_ADD
   {  double value      = value_      + other.value_;
      double derivative = derivative_ + other.derivative_;
      return ad_double(value, derivative);
   }
   //
   // BEGIN_SUB
   ad_double operator-(const ad_double& other) const
   // END_SUB
   {  double value       = value_      - other.value_;
      double derivative  = derivative_ - other.derivative_;
      return ad_double(value, derivative);
   }
   //
   // BEGIN_MUL
   ad_double operator*(const ad_double& other) const
   // END_MUL
   {  double value       = value_      * other.value_;
      double derivative  = value_      * other.derivative_
                         + derivative_ * other.value_;
      return ad_double(value, derivative);
   }
   //
   // BEGIN_DIV
   ad_double operator/(const ad_double& other) const
   // END_DIV
   {  double value       = value_      / other.value_;
      double derivative  = derivative_ / other.value_
         - value_ * other.derivative_ /(other.value_ * other.value_);
      return ad_double(value, derivative);
   }
};

/*
------------------------------------------------------------------------------
{xrst_begin example_ad_double}
{xrst_spell
   dx
}

An Example Using the ad_double Class
####################################
This example mixes the documentation and the example code.
Another choice is to put the documentation and the beginning
an then just have comments in the code.

xrst_indent
***********
This example make uses of ``xrst_indent`` so that
the xrst input can be indented at the same level as the code it is next to.

Begin Function
**************
This function has no arguments and returns a boolean that is true,
if all it's tests pass, and false otherwise.
{xrst_code cpp} */
bool test_ad_double(void)
{
/* {xrst_code}
   {xrst_indent}

   Initialize ok
   *************
   {xrst_code cpp} */
   bool ok = true;
   /* {xrst_code}

   Independent Variable
   ********************
   {xrst_code cpp} */
   double x  = 2.0;
   double dx = 3.0;
   ad_double ax(x, dx);
   /* {xrst_code}

   Addition
   ********
   {xrst_code cpp} */
   {  ad_double ay = ax + ax;
      double    dy = ay.derivative();
      ok          &= dy == 2.0 * dx;
   }
   /* {xrst_code}

   Subtraction
   ***********
   {xrst_code cpp} */
   {  ad_double ay = ax - ax;
      double    dy = ay.derivative();
      ok          &= dy == 0.0;
   }
   /* {xrst_code}

   Multiplication
   **************
   {xrst_code cpp} */
   {  ad_double ay = ax * ax;
      double    dy = ay.derivative();
      ok          &= dy == 2.0 * x * dx;
   }
   /* {xrst_code}

   Division
   ********
   {xrst_code cpp} */
   {  ad_double ay = ax / ax;
      double    dy = ay.derivative();
      ok          &= dy == 0.0;
   }
   /* {xrst_code}

   Return ok
   *********
{xrst_indent}
{xrst_code cpp} */
   return ok;
}
/* {xrst_code}

Example File
************
:ref:`class_example@This Example File`
is the same as for the parent of this page.
{xrst_end example_ad_double}
------------------------------------------------------------------------------
{xrst_begin test_ad_double}

Run ad_double Example and Check its Result
##########################################
{xrst_literal
   BEGIN_MAIN
   END_MAIN
}

Example File
************
:ref:`class_example@This Example File`
is the same as for the parent of this page.
{xrst_end test_ad_double}
*/
// BEGIN_MAIN
int main(void)
{  bool ok = test_ad_double();

   if( ! ok )
   {  std::cerr << "test_ad_double: Error\n";
      return 1;
   }
   std::cout << "test_ad_double: OK\n";
}
// END_MAIN
