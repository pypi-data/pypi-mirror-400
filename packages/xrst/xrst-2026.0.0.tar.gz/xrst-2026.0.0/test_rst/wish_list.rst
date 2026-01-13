.. _wish_list-name:

!!!!!!!!!
wish_list
!!!!!!!!!

.. meta::
   :keywords: wish_list,wish,list,spell,checking,theme,sphinx_rtd_theme,sphinx_book_theme,search,rst,command,file,names,tabs

.. index:: wish_list, wish, list

.. _wish_list-title:

Wish List
#########
The following is a wish list for future improvements to ``run_xrst``.
If you want to help with one of these, or some other aspect of xrst,
open an `xrst issue <https://github.com/bradbell/xrst/issues>`_ .

.. contents::
   :local:

.. index:: spell, checking

.. _wish_list@Spell Checking:

Spell Checking
**************

#. ``:ref:`` references that use the xrst ``-title`` should detect
   special words in the page name (similar to ``-name`` references).
   The corresponding check for double word error should use the page title
   instead of name because that is what the user sees.

#. Spell checking should not require a special word for any valid role names;
.e.g, the following text should not require a special spelling entry for
``samp`` ::

   :samp:`print 1+{variable}`

#. The spell checker should not check web addresses in external link
   definitions of the form ::

      .. external link name: external link web address

.. index:: theme

.. _wish_list@Theme:

Theme
*****
It would be nice to have better
:ref:`config_file@html_theme_options@Default` options for more themes
so that they work will with xrst.

.. index:: sphinx_rtd_theme

.. _wish_list@Theme@sphinx_rtd_theme:

sphinx_rtd_theme
================
It would be nice if there were a way to make this theme use more
horizontal space (currently xrst tires to modify its output to do this).

.. index:: sphinx_book_theme

.. _wish_list@Theme@sphinx_book_theme:

sphinx_book_theme
=================
It would be nice if the sphinx_book_theme did not use the full
width of the display for tables; see issue-807_  .

.. _issue-807: https://github.com/executablebooks/sphinx-book-theme/issues/807

.. index:: search

.. _wish_list@Search:

Search
******
It would be nice if we could make the sphinx search act like the
xrst search page (so we would not need two searches) .

.. index:: rst, names

.. _wish_list@RST Command File Names:

RST Command File Names
**********************
It would be nice if all commands in the rst files used file names
were automatically mapped so they were relative to the
:ref:`config_file@directory@project_directory` .
If this were the case, one would not need the
:ref:`dir command<dir_cmd-title>` .
In addition, the file names should not be checked for spelling
(this is already true for the ``ref`` role).

.. index:: tabs

.. _wish_list@Tabs:

Tabs
****
Tabs in xrst input is not tested.
