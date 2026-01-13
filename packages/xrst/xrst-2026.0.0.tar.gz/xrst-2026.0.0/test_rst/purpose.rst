.. _purpose-name:

!!!!!!!
purpose
!!!!!!!

.. meta::
   :keywords: purpose,of,this,sphinx,wrapper,motivation,goal,features

.. index:: purpose, sphinx, wrapper

.. _purpose-title:

Purpose of this Sphinx Wrapper
##############################

.. contents::
   :local:

.. index:: motivation

.. _purpose@Motivation:

Motivation
**********
This wrapper was motivated by cases like the GNU Scientific library,
which is written in C, uses sphinx for its documentation,
and has its documentation
in separate files from the corresponding source code; see::

   https://git.savannah.gnu.org/cgit/gsl.git/tree/doc

.. index:: goal

.. _purpose@Goal:

Goal
****
The goal is to extend RST and sphinx so that they can be
used in the comments of any source code language; i.e.,
once you learn xrst, you can use it for any source code language.
This wrapper differs from doxygen and autodoc in how
the user controls the sections of source code
that are part of the documentation and API; e.g., see
:ref:`class_example-name`.
The wrapper is easy to understand because it only
uses sphinx features available through the rst files.

.. index:: features

.. _purpose@Features:

Features
********
The xrst features below can be considered a wish list for sphinx:

#. Use a :ref:`toml file<config_file-name>`
   in place of the python file ``config.py`` .
   Also enable some sphinx options to change without changing the source code;
   see :ref:`run_xrst-name` .
#. Make it easy to put documentation in source code comments,
   even when multiple computer languages are used by one package;
   e.g., see :ref:`comment_ch_cmd-name` .
#. Multiple pages can be specified in one
   input file and one page can be the parent for the
   other pages in the same file; see :ref:`begin_cmd-name` .
#. One can build subsets of the documentation; e.g., examples, user, developer.
   Pages for different subsets can be in the
   same input file; see :ref:`run_xrst@group_list`.
#. The template command can use one file
   as the input in multiple places,
   with specialized text replacement for each use.
   See the discussion of how this differs from an
   :ref:`template_cmd@Rst Include` .
#. For each page, the rst file name ,
   :ref:`heading_links@Labels@Level Zero@page_name` ,
   is used as an abbreviated title in the navigation bar.
   This makes the navigation bar more useful.
   The first heading of a page is used as a longer and more descriptive
   :ref:`heading_links@Labels@Level Zero@page_title` .
#. Sphinx error messages are translated from rst file and line number
   to the file and line number in corresponding xrst input file.
   In addition, :ref:`run_xrst@page_source` is the xrst input,
   not the extracted rst file.
#. There are two levels to the table of contents. Each entry at the
   global level is a page name or title; e.g.,
   see the :ref:`xrst_contents-title` for this documentation.
   Each entry at the local level is a headings with in a page.
   The :ref:`run_xrst@local_toc` option can be used to display the second
   level for each page.
   Some sphinx themes display the global (local) table of contents on the
   left (right) side of each web page.
#. Words in each heading are automatically included in the
   index in a way that can be configured;
   see :ref:`config_file@not_in_index` .
   These words are also automatically included as html keyword meta data.
#. An additional xrst_search utility,
   that uses the keywords mentioned, above is included;
   see the link directly below the search utility that comes with sphinx.
#. A spell checker is included with special words at two levels;
   :ref:`spell_cmd-name` for the page level
   and :ref:`config_file@project_dictionary` for the project level.
   The spell checker catches double word errors.
#. Make it easier to include source code that executes
   directly below the current location;
   see the discussion of how this is different from the
   :ref:`code_cmd@code-block` directive.
#. Source code can also be included from multiple locations in any file;
   see the discussion of how this is different from the
   :ref:`literal_cmd@literalinclude` directive.
#. It is possible to document a feature using one language
   and implement the feature, right next to the documentation,
   using a different language; e.g., see :ref:`suspend_example-name` .
#. Automatically generate labels for linking to a heading in any page.
   These labels are designed with changing documentation in mind; e.g.,
   in this documentation the text
   ``:ref:``\ \`\ ``heading_links@Labels@Discussion``\ \`
   generates a link to :ref:`heading_links@Labels@Discussion`,
   which discusses these labels in more detail.
#. Allow for newlines in the target for a sphinx ``ref`` role;
   see :ref:`ref_example-name` and :ref:`ref_cmd-name` .
#. The :ref:`config_file@heading` configuration option
   can be used to check that all the pages in a project use the same
   underline and overline convention.
