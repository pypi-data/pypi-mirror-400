.. _heading_links-name:

!!!!!!!!!!!!!
heading_links
!!!!!!!!!!!!!

.. meta::
   :keywords: heading_links,heading,cross,reference,links,index,labels,level,zero,page_name,page_title,linking,text,other,levels,heading@to@label,label,to,anchor,discussion,example

.. index:: heading_links, heading, cross, reference, links

.. _heading_links-title:

Heading Cross Reference Links
#############################

.. contents::
   :local:

.. index:: index

.. _heading_links@Index:

Index
*****
For each word in a heading,
a link is included in the index from the word to the heading.
In addition, each word is added to the html keyword meta data
next to the page heading.

.. index:: labels

.. _heading_links@Labels:

Labels
******
A cross reference label is defined for linking
from anywhere to a heading. The details of how to use
these labels are described below.

.. index:: level, zero

.. _heading_links@Labels@Level Zero:

Level Zero
==========
Each :ref:`page<begin_cmd@page>` can have only one header at
the first level which is a title for the page.

.. index:: page_name

.. _heading_links@Labels@Level Zero@page_name:

page_name
---------
The input below will display the page name as the linking text:

  ``:ref:`` \` *page_name* ``-name`` \`

There is an exception to this, automatically generated pages
``xrst_search`` , ``xrst_index`` , and ``xrst_contents`` , do not include
the initial ``xrst_`` in the linking text; see
:ref:`auto_file@xrst_search.rst` , and
:ref:`auto_file@xrst_contents.rst` , and
:ref:`auto_file@xrst_index.rst` .

.. index:: page_title

.. _heading_links@Labels@Level Zero@page_title:

page_title
----------
The input below will display the page title as the linking text:

    ``:ref:`` \` *page_name* ``-title`` \`

.. index:: linking, text

.. _heading_links@Labels@Level Zero@Linking Text:

Linking Text
------------
You can also explicitly choose the linking text using:

   ``:ref:`` \` *linking_text* ``<`` *page_name* ``-name>`` \`

.. index:: other, levels

.. _heading_links@Labels@Other Levels:

Other Levels
============
The label for linking a heading that is not at level zero is the label
for the heading directly above it plus an at sign character :code:`@`,
plus the conversion for this heading.
These labels use the *page_name* for level zero,
without the ``-name`` or ``--title`` at the end.

.. index:: heading@to@label

.. _heading_links@Labels@Heading-To-Label:

Heading@To@Label
================
The conversion of a heading to a label
removes all backslashes ``\`` and changes at signs ``@``
to dashes ``-``.

For example, the label for the heading above is

   :ref:`heading_links@Labels@Heading-To-Label
   <heading_links@Labels@Heading-To-Label>`

The label corresponding to a header is used to reference the heading
using the ``:ref:`` role.

.. index:: label, anchor

.. _heading_links@Labels@Label To Anchor:

Label To Anchor
===============
There is a further conversion to create the
HTML anchor corresponding to a label.  To be specific:

1. The anchor is converted to lower case.
3. Characters that are not letters or decimal digits are converted to dashes.
4. Multiple dashes are converted to one dash.
5. The beginning of the anchor is trimmed until a letter is reached.
6. The end of the anchor is trimmed until a letter or digit is reached.

If for one page, these anchors are not unique, xrst reports an error.

.. index:: discussion

.. _heading_links@Labels@Discussion:

Discussion
==========
#. Note that for level zero one uses the *page_name* and not the
   title; e.g., in the example above one uses ``heading_links``
   and not ``Heading Cross Reference Links`` .
#. The ``@`` and not ``.`` character is used to separate levels
   because the ``.`` character is often used in titles and
   page names; e.g. :ref:`auto_file@conf.py`.
#. The xrst automatically generated labels end in ``-name`` , ``-title`` ,
   or have a ``@`` character in them. Other labels, that you create using
   rst commands, should not satisfy this condition
   (and hence are easy to distinguish).
#. Including all the levels above a heading in its label may seem verbose.

   #. This avoids ambiguity when the same heading appears twice in one page.
      For example, this link to the project name
      :ref:`config_file@project_name@Default`
      which is one of many Default headings on that page.
   #. It also helps keep the links up to date.
      If a heading changes, all the links to that heading, and all the
      headings below it, will break. This identifies the links that should be
      checked to make sure they are still valid.

#. It is an error for two headings have the same HTML anchor.
   This makes the html location of a heading valid as long as its label
   does not change. This is useful when posting the answer to a questions
   using a particular heading.
#. The html location of a heading does not depend on the location of its
   page in the documentation tree or the source code.
   Hence an html heading location is still valid after changing its
   documentation and/or source code locations.

.. _heading_links@Example:

Example
*******
:ref:`heading_example-name`
