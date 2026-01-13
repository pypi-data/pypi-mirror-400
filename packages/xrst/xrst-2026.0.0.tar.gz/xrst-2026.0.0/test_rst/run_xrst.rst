.. _run_xrst-name:

!!!!!!!!
run_xrst
!!!!!!!!

.. meta::
   :keywords: run_xrst,extract,rst,files,and,run,sphinx,syntax,version,local_toc,page_source,external_links,replace_spell_commands,ignore_spell_commands,suppress_spell_warnings,continue_with_warnings,rst_line_numbers,rst_only,index_page_name,config_file,xrst.toml,html_theme,theme,choices,sphinx_rtd_theme,target,tex,number_jobs,link_timeout,group_list,example,rename_group,old_group_name,new_group_name

.. index:: run_xrst, extract, rst, files, run, sphinx

.. _run_xrst-title:

Extract RST Files And Run Sphinx
################################

.. contents::
   :local:

.. _run_xrst@Syntax:

Syntax
******

| ``xrst`` \\
| |tab| [ ``--version`` ] \\
| |tab| [ ``--local_toc`` ] \\
| |tab| [ ``--page_source`` ] \\
| |tab| [ ``--external_links`` ] \\
| |tab| [ ``--replace_spell_commands`` ] \\
| |tab| [ ``--ignore_spell_commands`` ] \\
| |tab| [ ``--suppress_spell_warnings`` ] \\
| |tab| [ ``--continue_with_warnings`` ] \\
| |tab| [ ``--rst_line_numbers`` ] \\
| |tab| [ ``--rst_only`` ] \\
| |tab| [ ``--index_page_name`` *index_page_name* ] \\
| |tab| [ ``--config_file``     *config_file* ] \\
| |tab| [ ``--html_theme``      *html_theme* ] \\
| |tab| [ ``--target``          *target* ]  \\
| |tab| [ ``--number_jobs``     *number_jobs* ] \\
| |tab| [ ``--link_timeout``    *link_timeout* ] \\
| |tab| [ ``--group_list``      *group_name_1* *group_name_2* ... ] \\
| |tab| [ ``--rename_group``    *old_group_name* *new_group_name* ] \\

#. The brackets around each of lines above indicate that the line is optional.
#. The lines above can appear in any order.
#. Text in code font; e.g. ``--target`` is explicit; i.e.,
   must appear exactly as above.
#. Text in italic font; .e.g, *target* is implicit; i.e.,
   it gets replaced by the user's choice.
#. It may be helpful to remove the :ref:`config_file@directory@html_directory`
   before running the command below.
   This will check for error messages that are not repeated due
   to caching the results of previous builds.

.. index:: version

.. _run_xrst@version:

version
*******
If ``--version`` is present on the command line,
the version of xrst is printed and none of the other arguments matter.

.. index:: local_toc

.. _run_xrst@local_toc:

local_toc
*********
If this option is present on the command line,
a table of contents for the Headings in the current page
is included at the top of every page.
The page name and page title are not in this table of contents.

Some :ref:`html themes<run_xrst@html_theme>` include this information
on a side bar; e.g., ``furo`` and ``sphinx_book_theme`` .

.. index:: page_source

.. _run_xrst@page_source:

page_source
***********
If this option is present and *target* is ``html`` ,
a link to the xrst source code is included at the top of each page.
Some :ref:`html themes<run_xrst@html_theme>` include this link; e.g.,
``sphinx_rtd_theme`` .

If this option is present and *target* is ``tex`` ,
the xrst source code file is reported at the beginning of each page.

.. index:: external_links

.. _run_xrst@external_links:

external_links
**************
If this option is present, the external links are checked.
The ones that are broken or redirects are reported.
Broken links are considered errors and redirects are warnings.

.. index:: replace_spell_commands

.. _run_xrst@replace_spell_commands:

replace_spell_commands
**********************
If this option is present on the command line, the source code
:ref:`spell commands<spell_cmd-name>` are replaced in such a way that the
there will be no spelling warnings during future processing by xrst.
If this option is present,
none of the output files are created; e.g., the \*.rst and \*.html files.

#. This is useful when there are no spelling warnings before a change
   to the :ref:`config_file@project_dictionary` or when there is an update
   to the :ref:`config_file@spell_package` .
#. This is also useful when there are no spelling warnings and you want
   to sort the words in all the spelling commands.

See also :ref:`config_file@project_dictionary` .

.. index:: ignore_spell_commands

.. _run_xrst@ignore_spell_commands:

ignore_spell_commands
*********************
If this option is present on the command line, the
:ref:`spell commands<spell_cmd-name>` are ignored and
none of the output files are created; e.g., the \*.rst and \*.html files.

#. This can be used to find words that should be added to the
   :ref:`config_file@project_dictionary` ; i.e.,
   words in error and with a high page count .
#. If you remove a word from the project dictionary, this can be used
   to check how many pages use that word.

If you change the project dictionary consider using
:ref:`run_xrst@replace_spell_commands` .

.. index:: suppress_spell_warnings

.. _run_xrst@suppress_spell_warnings:

suppress_spell_warnings
***********************
If this option is present on the command line, none of the spelling warnings
will be generated.
This is useful when there are no spelling warnings with one spelling package
and you are temporarily using a different version of the package
or a different package altogether.

.. index:: continue_with_warnings

.. _run_xrst@continue_with_warnings:

continue_with_warnings
**********************
If this option is (is not) present on the command line,
the program will not exit (will exit) with an error when warnings are
generated.

.. index:: rst_line_numbers

.. _run_xrst@rst_line_numbers:

rst_line_numbers
****************
Normally sphinx error and warning messages are reported using line numbers
in the xrst source code files.
If this option is present, these messages are reported
using the line numbers in the RST files created by xrst.
In addition the :ref:`run_xrst@page_source` links to the rst files,
instead of the xrst source files.
This may be helpful if you have an error or warning for a sphinx command
and it does not make sense using xrst source code line numbers.
It is also helpful for determining if an incorrect line number is due to
sphinx or xrst.

.. index:: rst_only

.. _run_xrst@rst_only:

rst_only
********
Normally, after extraction the RST files,
xrst automatically runs sphinx to produce the target output (html or tex).
If this option is present, sphinx is not run.
Only the rst files, and their corresponding sources,
are generated; i.e.,

| |tab| :ref:`config_file@directory@rst_directory`/\*.rst
| |tab| *rst_directory*\ /_sources/\*.txt

This may be useful when creating rst files for uses else where; e.g.,
for use with `Read the Docs <https://docs.readthedocs.com/platform/stable>`_
(see :ref:`.readthedocs.yaml-name` for a better way to use Read the Docs.)
The sphinx commands are printed after xrst finishes and can be executed
by hand.
This may be useful if there is a problem during these commands.

.. index:: index_page_name

.. _run_xrst@index_page_name:

index_page_name
***************
This option has no effect when *target* is ``tex`` .
If *target* is ``html``,
the file ``index.html`` in the
:ref:`config_file@directory@html_directory` will be a redirect
to the page specified by *index_page_name* .
If this option is not present, ``index.html`` wil be a redirect
to the root of the documentation tree.

.. index:: config_file

.. _run_xrst@config_file:

config_file
***********
The command line argument *config_file* specifies the location of the
:ref:`config_file-name` for this project.
This can be an absolute path or
relative to the directory where :ref:`xrst<run_xrst-name>` is run.

.. index:: xrst.toml

.. _run_xrst@config_file@xrst.toml:

xrst.toml
=========
If *config_file* is not present on the command line,
the default value ``xrst.toml`` is used for *config_file* .

.. index:: html_theme

.. _run_xrst@html_theme:

html_theme
**********
This the html_theme_ that is used.
The default value for *html_theme* is ``furo`` .
You may need to use pip to install other themes that you use.

.. _html_theme: https://sphinx-themes.org/

.. index:: theme, choices

.. _run_xrst@html_theme@Theme Choices:

Theme Choices
=============
The following is a list of some themes that work well with the
default settings in :ref:`config_file@html_theme_options` .
If you have a theme together with html_theme_options
that work well with xrst,
please post an issue on github so that it can be added to the list below.

.. csv-table:: Sphinx Themes
   :header: name,  local_toc

   sphinx_rtd_theme,     yes
   furo,                 no
   sphinx_book_theme,    no
   pydata_sphinx_theme,  no
   piccolo_theme,        no

.. index:: sphinx_rtd_theme

.. _run_xrst@html_theme@sphinx_rtd_theme:

sphinx_rtd_theme
================
The sphinx_rtd theme builds faster than some of the other themes,
so it is suggested to use it for testing (with the ``--local_toc`` option).
A special modification is made to this theme when *target* is html,
so that it displays wider than its normal limit.
This modification may be removed in the future.

.. index:: target

.. _run_xrst@target:

target
******
The command line argument *target* must be ``html`` or ``tex``.
It specifies the type of type output you plan to generate using sphinx.
Note thet :ref:`config_file@directory@html_directory` and
:ref:`config_file@directory@tex_directory` will determine the location
of the corresponding output files.
The default value for *target* is ``html`` .

.. index:: tex

.. _run_xrst@target@tex:

tex
===
If you choose this target, xrst will create the file
*project_name*\ ``.tex`` in the :ref:`config_file@directory@tex_directory` .
There are two reasons to build this file.
One is to create the file *project_name*\ ``.pdf``
which is a pdf version of the documentation.
The other is to test for errors in the latex sections of the documentation.
(MathJax displays latex errors in red, but one has to check
every page that has latex to find all the errors this way.)
Once you have built *project_name*\ ``.tex``, the following command
executed in :ref:`config_file@directory@project_directory`
will accomplish both purposes:

   make -C *tex_directory* *project_name*\ ``.pdf``

#. The :ref:`config_file@project_name` is specified in the configuration file.
#. The resulting output file will be *project*\ ``.pdf`` in the
   *tex_directory* .
#. If a Latex error is encountered, the pdf build will stop with a message
   at the ``?`` prompt. If you enter ``q`` at this prompt, it will complete
   its processing in batch mode. You will be able to find the error messages
   in the file *project_name*\ ``.log`` in the *tex_directory* .
#. Translating Latex errors to the corresponding xrst input file:

   #. Latex error messages are reported using line numbers in
      the file *project*\ ``.tex`` .
   #. You may be able to find the corresponding xrst input file
      using by using ``grep`` to find text that is near the error.
   #. The page numbers in the :ref:`xrst_contents-title` are
      present in the latex input (often near ``section*{`` above the error)
      and may help translate these line numbers to page names.
   #. Given a page name, the corresponding xrst input file can
      be found at the top of the html version of the page.

.. index:: number_jobs

.. _run_xrst@number_jobs:

number_jobs
***********
This is a positive integer specifying the number of parallel jobs
that xrst is allowed to use.
The default value for *number_jobs* is ``1`` .

.. index:: link_timeout

.. _run_xrst@link_timeout:

link_timeout
************
This is a positive integer specifying the number of seconds that the sphinx
link check builder will wait for a response after each hyperlink request.
This only has an affect if :ref:`run_xrst@external_links` is present.
The default value for *link_timeout* is 30 .

.. index:: group_list

.. _run_xrst@group_list:

group_list
**********
It is possible to select one or more groups of pages
to include in the output using this argument.

#. The *group_list* is a list of one or more
   :ref:`group names<begin_cmd@group_name>`.
#. The :ref:`begin_cmd@group_name@Default Group` is represented by
   the group name ``default`` .
#. The order of the group names determines their order in the resulting output.
#. The default value for *group_list* is ``default`` .

For each group name in the *group_list*
there must be an entry in :ref:`config_file@root_file` specifying the
root file for that group name.

The xrst examples are a subset of its user documentation
and its user documentation is a subset of its developer documentation.
For each command, the same source code file provides both the
user and developer documentation. In addition, the developer documentation
has links to the user documentation and the user documentation has links
to the examples.

.. _run_xrst@group_list@Example:

Example
=======
The examples commands below assume you have cloned the
`xrst git repository <https://github.com/bradbell/xrst>`_
and it is your current working directory.

#. The xrst examples use the default group
   and their documentation can be built using

      ``xrst --group_list default``

#. The xrst user documentation uses the default and user groups
   and its documentation can be built using

      ``xrst --group_list default user``

#. The xrst developer documentation uses the default, user, and dev
   groups and its documentation can be built using

      ``xrst --group_list default user dev``

.. index:: rename_group

.. _run_xrst@rename_group:

rename_group
************
If this option is present on the command line,
the :ref:`begin_cmd@group_name` in a subset of the source code, is changed.
This option replaces the :ref:`run_xrst@group_list`
by the list whose only entry is *new_group_name* .
None of the output files are created when rename_group is present;
e.g., the \*.rst and \*.html files.

.. index:: old_group_name

.. _run_xrst@rename_group@old_group_name:

old_group_name
==============
is the old group name for the pages that will have their group name replaced.
Use ``default``, instead of the empty group name, for the
:ref:`begin_cmd@group_name@Default Group` .

.. index:: new_group_name

.. _run_xrst@rename_group@new_group_name:

new_group_name
==============
Only the pages below the :ref:`config_file@root_file`
for *new_group_name* are modified.
You can rename a subset of the old group by making the root file
for the new group different than the root file for the old group.
Each page in the old group, and below the root file for the new group,
will have its group name changed from *old_group_name* to *new_group_name*.
Use ``default``, instead of the empty group name, for the
:ref:`begin_cmd@group_name@Default Group` .
