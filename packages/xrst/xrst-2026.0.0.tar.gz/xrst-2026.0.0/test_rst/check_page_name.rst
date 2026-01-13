.. _check_page_name-name:

!!!!!!!!!!!!!!!
check_page_name
!!!!!!!!!!!!!!!

.. meta::
   :keywords: check_page_name,check,the,rules,for,a,page,name,page_name,file_name,m_obj,data,prototype

.. index:: check_page_name, check, rules, page, name

.. _check_page_name-title:

Check the rules for a page name
###############################

.. contents::
   :local:

.. index:: page_name

.. _check_page_name@page_name:

page_name
*********
The page_name appears in *m_obj* in one of the following ways

#.  {xrst_begin_parent page_name user}
#.  {xrst_begin page_name user}
#.  {xrst_end page_name}

A valid page name must satisfy the following conditions:

#.  The valid characters in a page name are [A-Z], [a-z], [0-9],
    dash, period and underbar.
#.  A page name cannot begin with ``xrst_`` .
#.  A page name cannot be ``index`` or ``genindex`` .

If *page_name* does not follow
these rules, a message is printed and the program exits.

.. index:: file_name

.. _check_page_name@file_name:

file_name
*********
is the name of the original input file that data appears in
(used for error reporting).

.. index:: m_obj

.. _check_page_name@m_obj:

m_obj
*****
is the match object corresponding to *page_name*

.. index:: data

.. _check_page_name@data:

data
****
is that data that was searched to get the match object.

.. index:: prototype

.. _check_page_name@Prototype:

Prototype
*********

.. literalinclude:: ../../xrst/check_page_name.py
   :lines: 62-66
   :language: py
