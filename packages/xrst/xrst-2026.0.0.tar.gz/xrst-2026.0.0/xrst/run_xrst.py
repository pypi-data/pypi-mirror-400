# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: Bradley M. Bell <bradbell@seanet.com>
# SPDX-FileContributor: 2020-26 Bradley M. Bell
# ----------------------------------------------------------------------------
r"""
{xrst_begin run_xrst user}
{xrst_spell
   dev
   furo
   github
   grep
   jax
   pdf
   rtd
   thet
   txt
   wil
}

Extract RST Files And Run Sphinx
################################

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

{xrst_comment --------------------------------------------------------------- }

version
*******
If ``--version`` is present on the command line,
the version of xrst is printed and none of the other arguments matter.
{xrst_comment --------------------------------------------------------------- }

local_toc
*********
If this option is present on the command line,
a table of contents for the Headings in the current page
is included at the top of every page.
The page name and page title are not in this table of contents.

Some :ref:`html themes<run_xrst@html_theme>` include this information
on a side bar; e.g., ``furo`` and ``sphinx_book_theme`` .
{xrst_comment --------------------------------------------------------------- }

page_source
***********
If this option is present and *target* is ``html`` ,
a link to the xrst source code is included at the top of each page.
Some :ref:`html themes<run_xrst@html_theme>` include this link; e.g.,
``sphinx_rtd_theme`` .

If this option is present and *target* is ``tex`` ,
the xrst source code file is reported at the beginning of each page.

external_links
**************
If this option is present, the external links are checked.
The ones that are broken or redirects are reported.
Broken links are considered errors and redirects are warnings.

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

suppress_spell_warnings
***********************
If this option is present on the command line, none of the spelling warnings
will be generated.
This is useful when there are no spelling warnings with one spelling package
and you are temporarily using a different version of the package
or a different package altogether.
{xrst_comment --------------------------------------------------------------- }

continue_with_warnings
**********************
If this option is (is not) present on the command line,
the program will not exit (will exit) with an error when warnings are
generated.
{xrst_comment --------------------------------------------------------------- }

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
{xrst_comment --------------------------------------------------------------- }

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
{xrst_comment --------------------------------------------------------------- }

index_page_name
***************
This option has no effect when *target* is ``tex`` .
If *target* is ``html``,
the file ``index.html`` in the
:ref:`config_file@directory@html_directory` will be a redirect
to the page specified by *index_page_name* .
If this option is not present, ``index.html`` wil be a redirect
to the root of the documentation tree.
{xrst_comment --------------------------------------------------------------- }

config_file
***********
The command line argument *config_file* specifies the location of the
:ref:`config_file-name` for this project.
This can be an absolute path or
relative to the directory where :ref:`xrst<run_xrst-name>` is run.

xrst.toml
=========
If *config_file* is not present on the command line,
the default value ``xrst.toml`` is used for *config_file* .
{xrst_comment --------------------------------------------------------------- }

html_theme
**********
This the html_theme_ that is used.
The default value for *html_theme* is ``furo`` .
You may need to use pip to install other themes that you use.

.. _html_theme: https://sphinx-themes.org/

Theme Choices
=============
The following is a list of some themes that work well with the
default settings in :ref:`config_file@html_theme_options` .
If you have a theme together with html_theme_options
that work well with xrst,
please post an issue on github so that it can be added to the list below.

{xrst_spell_off}
.. csv-table:: Sphinx Themes
   :header: name,  local_toc

   sphinx_rtd_theme,     yes
   furo,                 no
   sphinx_book_theme,    no
   pydata_sphinx_theme,  no
   piccolo_theme,        no
{xrst_spell_on}

sphinx_rtd_theme
================
The sphinx_rtd theme builds faster than some of the other themes,
so it is suggested to use it for testing (with the ``--local_toc`` option).
A special modification is made to this theme when *target* is html,
so that it displays wider than its normal limit.
This modification may be removed in the future.
{xrst_comment --------------------------------------------------------------- }

target
******
The command line argument *target* must be ``html`` or ``tex``.
It specifies the type of type output you plan to generate using sphinx.
Note thet :ref:`config_file@directory@html_directory` and
:ref:`config_file@directory@tex_directory` will determine the location
of the corresponding output files.
The default value for *target* is ``html`` .

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
{xrst_comment --------------------------------------------------------------- }

number_jobs
***********
This is a positive integer specifying the number of parallel jobs
that xrst is allowed to use.
The default value for *number_jobs* is ``1`` .

link_timeout
************
This is a positive integer specifying the number of seconds that the sphinx
link check builder will wait for a response after each hyperlink request.
This only has an affect if :ref:`run_xrst@external_links` is present.
The default value for *link_timeout* is 30 .

{xrst_comment --------------------------------------------------------------- }

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
{xrst_comment --------------------------------------------------------------- }

rename_group
************
If this option is present on the command line,
the :ref:`begin_cmd@group_name` in a subset of the source code, is changed.
This option replaces the :ref:`run_xrst@group_list`
by the list whose only entry is *new_group_name* .
None of the output files are created when rename_group is present;
e.g., the \*.rst and \*.html files.

old_group_name
==============
is the old group name for the pages that will have their group name replaced.
Use ``default``, instead of the empty group name, for the
:ref:`begin_cmd@group_name@Default Group` .

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
{xrst_comment --------------------------------------------------------------- }

{xrst_end run_xrst}
"""
# ---------------------------------------------------------------------------
# imports
# ---------------------------------------------------------------------------
import sys
import re
import os
import string
import shutil
import filecmp
import argparse
import subprocess
import platform
import importlib.util
# ---------------------------------------------------------------------------
# system_exit
# Error messages in this file do not use xrst.system_exit because
# they do not have file names that are relative to the project_directory.
def system_exit(msg) :
   # assert False, msg
   sys.exit(msg)
# ---------------------------------------------------------------------------
# Execute a system command
#
# command:
# the command to execute
#
# warning:
# If a warning is printed, this flag is set True
#
# page_name2line_tuple
# a mapping from page name to to a list of line number pairs.
# The first number is the pair is a line number in the rst file for this page.
# The second number is a corresponding xrst input line number.
#
# page_name2page_file
# map page name to the xrst input file that contains its begin command.
#
def system_command(
      command                    ,
      warning                    ,
      page_name2line_tuple = None ,
      page_name2page_file  = None ,
) :
   assert type(command) == str
   #
   assert type(warning) == list
   assert len(warning) == 1
   assert type(warning[0]) == bool
   #
   if page_name2line_tuple != None :
      assert type(page_name2line_tuple) == dict
      assert type(page_name2page_file) == dict
   #
   # build_link
   build_html = command.startswith('sphinx-build -b html')
   build_tex  = command.startswith('sphinx-build -b latex')
   build_link = command.startswith('sphinx-build -b linkcheck')
   assert build_html or build_tex or build_link
   #
   # subprocess.run, stderr
   print(command)
   command = command.split(' ')
   result = subprocess.run(command, capture_output = True)
   stderr = result.stderr.decode('utf-8')
   #
   # alert_data, pattern_alert
   if build_html or build_tex :
      #
      # alert_data
      alert_data = stderr
      #
      # PAGE_NAME_PATTERN = [A-Za-z0-9._-]+
      # use git grep PAGE_NAME_PATTERN to get all occurrences of this pattern
      pattern_alert = re.compile(
         r'.*/rst/([A-Za-z0-9_.-]+).rst:([0-9]+):([^:]*):'
      )
   else :
      assert build_link
      #
      # alert_data
      target_directory = command[-1]
      file_obj         = open( f'{target_directory}/output.txt' , 'r')
      alert_data       = file_obj.read()
      file_obj.close()
      if alert_data == '' :
         alert_data = stderr
      else :
         alert_data = stderr + '\n' + alert_data
      #
      # pattern_alert
      pattern_alert = re.compile( r'^([A-Za-z0-9_.-]+).rst:([0-9]+):' )
   #
   ok  =  result.returncode == 0 and alert_data == ''
   if ok :
      return
   #
   if page_name2line_tuple == None :
      message  = alert_data
      if result.returncode == 0 :
         message  += '\nWarning: see message above.\n'
         sys.stderr.write(message)
         warning[0] = True
         return
      else :
         message  += '\nError: see message above.'
         system_exit(message)
   #
   # message
   message = ''
   #
   # warn_not_xrst_label
   warn_not_xrst_label = True
   #
   # sphinx_error
   sphinx_error = result.returncode != 0
   #
   # alert_list
   alert_list = alert_data.split('\n')
   while '' in alert_list :
      alert_list.remove('')
   if len(alert_list) > 0 :
      if alert_list[-1].strip() == 'warnings.warn(' :
         alert_list.pop(-1)
   #
   # MacOS has a security warning
   if len(alert_list) == 1 :
      issue_320 = 'https://github.com/urllib3/urllib3/issues/3020'
      if alert_list[0].find(issue_320) != -1 :
         uname = platform.uname().system
         if uname == 'Darwin' :
            message  = 'MacOS python has an issue; see '
            message += issue_320 + '\n'
            sys.stderr.write(message)
            return
   #
   for alert in alert_list :
      #
      # m_alert
      m_alert = pattern_alert.search(alert)
      if m_alert == None :
         # this line is more info about previous line
         pass
      else :
         #
         # sphinx_error
         if build_html or build_tex:
            sphinx_error |= m_alert.group(3).strip() == 'ERROR'
         #
         # page_name
         page_name = m_alert.group(1)
         if not page_name in page_name2line_tuple :
            msg  = f'Cannot map line numbers for page {page_name}\n'
            msg += 'to its xrst input file and line number:\n'
            msg += alert
            msg += '\nTry removing the html output directory and re-run.'
            system_exit(msg)
         else :
            #
            # rst_line
            rst_line  = int( m_alert.group(2) )
            #
            # page_file, line_tuple
            page_file  = page_name2page_file[page_name]
            line_tuple = page_name2line_tuple[page_name]
            #
            # n_tuple
            n_tuple = len(line_tuple)
            #
            # index
            index  = 0
            while index < n_tuple and line_tuple[index][0] < rst_line :
                  index += 1
            assert len(line_tuple[index]) == 2 or len(line_tuple[index]) == 4
            #
            # line_before, line_after
            if index == n_tuple :
               line_before = str( line_tuple[n_tuple-1][1] )
               line_after  = '?'
            elif line_tuple[index][0] == rst_line :
               line_before = line_tuple[index][1]
               line_after  = line_tuple[index][1]
            elif 0 == index :
               line_before = '?'
               line_after  = line_tuple[index][1]
            else :
               line_before = line_tuple[index-1][1]
               line_after  = line_tuple[index][1]
            #
            # alert
            msg   = alert[ m_alert.end()  : ]
            if build_html or build_tex :
               msg = m_alert.group(3) + ':' + msg
            if line_before == line_after :
               alert = f'{page_file}:{line_before}:'
            else :
               alert = f'{page_file}:{line_before}-{line_after}:'
            if len( line_tuple[index] ) == 4 :
               template_file = line_tuple[index][2]
               template_line = line_tuple[index][3]
               alert += f'{template_file}:{template_line}:'
            alert += msg
      #
      # alert
      pattern_undefined = re.compile(r"undefined *label: *'([^']*)'")
      m_undefined       = pattern_undefined.search(alert)
      if m_undefined != None :
         label      = m_undefined.group(1)
         xrst_label = 0 < label.find('@')
         if label.endswith('-name') or label.endswith('-title') :
            xrst_label = True
         if not xrst_label and warn_not_xrst_label :
            warn_not_xrst_label = False
            alert += '\n   The label above does not contain an @'
            alert += ' or end with -name or -title.'
            alert += '\n   Hence it is not automatically generated by xrst.'
         if label == 'xrst_table_of_contents-title' :
            alert += '\n   2024-03-04: The label above was changed to'
            alert += " 'xrst_contents-title'"
      #
      # message
      if alert != '' :
         message += '\n' + alert
   #
   if sphinx_error :
      message  += '\nError: see messages above.'
      system_exit(message)
   #
   message  += '\nWarning: see messages above.\n'
   sys.stderr.write(message)
   warning[0] = True
   return
# ---------------------------------------------------------------------------
def fix_latex(latex_dir, project_name) :
   assert type(latex_dir) == str
   assert type(project_name) == str
   #
   # file_name
   file_name = f'{latex_dir}/{project_name}.tex'
   #
   # file_data
   file_obj  = open(file_name, 'r')
   file_data = file_obj.read()
   file_obj.close()
   #
   # file_data
   pattern   = re.compile( r'\n\\section{' )
   file_data = pattern.sub( r'\n\\section*{', file_data)
   #
   # file_data
   pattern   = re.compile( r'\n\\subsection{' )
   file_data = pattern.sub( r'\n\\subsection*{', file_data)
   #
   # file_data
   pattern   = re.compile( r'\n\\subsubsection{' )
   file_data = pattern.sub( r'\n\\subsubsection*{', file_data)
   #
   # file_name
   file_obj  = open(file_name, 'w')
   file_obj.write(file_data)
   file_obj.close()
   #
   return
# ---------------------------------------------------------------------------
# sys.path
# used so that we can test before installing
if( os.getcwd().endswith('/xrst.git') ) :
   if( os.path.isdir('xrst') ) :
      sys.path.insert(0, os.getcwd() )
#
import xrst
#
# version
version = '2026.0.0'
#
def run_xrst() :
   #
   # execution_directory
   execution_directory = os.getcwd()
   #
   # parser
   parser = argparse.ArgumentParser(
      prog='xrst', description='extract Sphinx RST files'
   )
   # --version
   parser.add_argument('--version', action='store_true',
      help='just print version of xrst'
   )
   # --local_toc
   parser.add_argument('--local_toc', action='store_true',
      help='add a local table of contents at the top of each page'
   )
   # --page_source
   parser.add_argument('--page_source', action='store_true',
      help='add link to the xrst source code be included at top of each page'
   )
   # --external_links
   parser.add_argument('--external_links', action='store_true',
      help='report external links that are broken or redirects'
   )
   # --replace_spell_commands
   parser.add_argument('--replace_spell_commands', action='store_true',
      help='replace the xrst spell commands in source code files'
   )
   # --ignore_spell_commands
   parser.add_argument('--ignore_spell_commands', action='store_true',
      help='ignore the xrst spell commands in source code files'
   )
   # --suppress_spell_warnings
   parser.add_argument('--suppress_spell_warnings', action='store_true',
      help='do not generate any of the spell checker wrnings'
   )
   # --continue_with_warning
   parser.add_argument('--continue_with_warnings', action='store_true',
      help='do not exit with an error when warnings are generated'
   )
   # --rst_line_numbers
   parser.add_argument('--rst_line_numbers', action='store_true',
      help='report sphinx errors and warnings using rst file line numbers'
   )
   # --rst_only
   parser.add_argument('--rst_only', action='store_true',
      help='Only extract the sphinx rst files; i.e., do not run sphinx.'
   )
   # --index_page_name
   parser.add_argument(
      '--index_page_name', metavar='index_page_name', default='xrst_root_doc',
      help='The file index.html will be a redirect to this page' + \
         '(default is root of documentation tree)'
   )
   # --config_file
   parser.add_argument(
      '--config_file', metavar='config_file', default='xrst.toml',
      help='location of the xrst configuration file which is in toml format' + \
         '(default is .)'
   )
   # --html_theme
   parser.add_argument(
      '--html_theme', metavar='html_theme', default='furo',
      help='sphinx html_theme that is used to display web pages ' + \
         '(default is furo)',
   )
   # --target
   parser.add_argument(
      '--target', metavar='target', choices=['html', 'tex'], default='html',
      help='type of output files, choices are html or tex (default is html)'
   )
   # --number_jobs
   parser.add_argument(
      '--number_jobs', metavar='number_jobs', default='1',
      help='number of parallel jobs xrst is allowed to use (default is 1)'
   )
   # --link_timeout
   parser.add_argument(
      '--link_timeout', metavar='link_timeout', default='30',
      help='seconds to wait for each external link check (default 30)'
   )
   # --group_list
   parser.add_argument(
      '--group_list', nargs='+', default='default',
      metavar= 'group_name' ,
      help='list of group_names to include in this build (default is default)'
   )
   # rename_group
   parser.add_argument(
      '--rename_group', nargs=2, default=None,
      metavar=('old_group_name', 'new_group_name'),
      help='change group name for pages below root page for new_group_name' \
         + '(no default)'
   )
   #
   # arguments
   arguments = parser.parse_args()
   #
   if arguments.version :
      print(version)
      sys.exit(0)
   #
   # local_toc
   local_toc = arguments.local_toc
   #
   # page_source
   page_source = arguments.page_source
   #
   # external_links
   external_links = arguments.external_links
   #
   # index_page_name
   index_page_name = arguments.index_page_name
   #
   # config_file
   # can not use system_exit until os.getcwd() returns project_directory
   config_file = arguments.config_file
   if not os.path.isfile(config_file) :
      msg  = 'xsrst: Error\n'
      msg += f'config_file = {config_file}\n'
      if config_file[0] == '/' :
         msg += 'is not a file\n'
      else :
         msg += f'is not a file relative to the execution directory\n'
         msg += execution_directory
      system_exit(msg)
   #
   # conf_dict
   conf_dict  = xrst.get_conf_dict(config_file)
   #
   # config_dir
   index = config_file.rfind('/')
   if 0 <= index :
      config_dir = config_file[: index]
      os.chdir(config_dir)
   #
   # project_directory
   project_directory = conf_dict['directory']['project_directory']
   #
   # make project directory the current working directory
   os.chdir(project_directory)
   #
   # replace_spell_commands
   replace_spell_commands = arguments.replace_spell_commands
   #
   # ignore_spell_commands
   ignore_spell_commands = arguments.ignore_spell_commands
   #
   # suppress_spell_warnings
   suppress_spell_warnings = arguments.suppress_spell_warnings
   #
   # continue_with_warnings
   continue_with_warnings = arguments.continue_with_warnings
   #
   # rst_line_numbers
   rst_line_numbers = arguments.rst_line_numbers
   #
   # rst_only
   rst_only = arguments.rst_only
   #
   # html_theme
   html_theme = arguments.html_theme
   spec  =  importlib.util.find_spec(html_theme)
   if spec == None :
      msg  = f'The html_theme is {html_theme} but cannot import {html_theme}'
      msg += f'\nPerhaps need to execute: pip install {html_theme}'
      sys.exit(msg)
   #
   # number_jobs
   number_jobs = int( arguments.number_jobs )
   if number_jobs <= 0 :
      msg = 'xrst number_jobs is less than or equal zero.'
      system_exit(msg)
   #
   # link_timeout
   link_timeout = int( arguments.link_timeout )
   if link_timeout <= 0 :
      msg = 'xrst link_timeout is less than or equal zero.'
      system_exit(msg)
   #
   # group_list
   group_list = arguments.group_list
   if type(group_list) == str :
      group_list = [ group_list ]
   #
   # rename_group, group_list
   rename_group = arguments.rename_group
   if rename_group != None :
      group_list = [ rename_group[1] ]
      #
      if rename_group[0] == '' :
         msg = 'xrst rename_group: old_group_name is empty.\n'
         msg += 'Use "default" for the empty group name.'
         system_exit(msg)
      if rename_group[1] == '' :
         msg = 'xrst rename_group: new_group_name is empty.\n'
         msg += 'Use "default" for the empty group name.'
         system_exit(msg)
   #
   # replace_spell_commands or rename_group
   if replace_spell_commands or rename_group != None :
      if replace_spell_commands :
         option = 'replace_spell_commands'
      else :
         option = 'rename_group'
      #
      cwd      = os.getcwd()
      prompt   = f'\nThe {option} option will change some of \n'
      prompt  += 'the files read by xrst. Make sure that you have a backup\n'
      prompt  += f'of source files in {cwd}\n'
      prompt  += 'before contining this operation: continue [yes/no] ? '
      response = None
      while response not in [ 'yes', 'no' ]:
         response = input(prompt)
      if response != 'yes' :
         system_exit( f'xrst: aborting {option}' )
   #
   # target
   target = arguments.target
   #
   # target_directory
   if target == 'html' :
      target_directory = conf_dict['directory']['html_directory']
   else :
      assert target == 'tex'
      target_directory = conf_dict['directory']['tex_directory']
   #
   # rst_directory
   rst_directory = conf_dict['directory']['rst_directory']
   if rst_directory[0] == '/' :
      msg  = 'rst_directory = ' + rst_directory + '\n'
      msg += 'must be a path relative to the project_directory'
      xrst.system_exit(msg)
   #
   if not os.path.isdir(rst_directory) :
      os.makedirs(rst_directory)
   #
   # rst2project_directory
   # relative path from the rst_directory to the project directory
   rst2project_directory = os.path.relpath(
      os.getcwd() , rst_directory
   )
   #
   # tmp_dir
   tmp_dir = rst_directory + '/tmp'
   if os.path.isdir(tmp_dir) :
      shutil.rmtree(tmp_dir)
   os.mkdir(tmp_dir)
   #
   # _sources
   if not os.path.isdir(rst_directory + '/_sources') :
      os.mkdir(rst_directory + '/_sources')
   #
   # spell_checker
   spell_list  = list()
   for entry in conf_dict['project_dictionary']['data'] :
      word_list = entry.split('\n')
      for word in word_list :
         word = word.strip(' \t')
         if len(word) > 0 :
            spell_list.append(word)
   package       = conf_dict['spell_package']['data']
   spell_checker = xrst.get_spell_checker(spell_list, package)
   #
   # not_in_index_list
   not_in_index_list = list()
   for entry in conf_dict['not_in_index']['data'] :
      pattern_list = entry.split('\n')
      for pattern in pattern_list :
         pattern = pattern.strip(' \t')
         try :
            not_in_index_list.append( re.compile(pattern) )
         except :
            msg  = f'not_in_index table in config_file = {config_file}\n'
            msg += f'The regular expression "{pattern}" would not compile'
            system_exit(msg)
   # -------------------------------------------------------------------------
   #
   # input_file_list
   input_file_list = None
   #
   # root_file
   root_file = conf_dict['root_file']
   #
   # project_name
   project_name = conf_dict['project_name']['data']
   #
   # all_page_info
   # This list accumulates over all the group names
   all_page_info  = list()
   #
   # root_page_list
   # Each group has a root section (in root_file) at the top if its tree.
   root_page_list = list()
   #
   # page_name2line_tuple, page_name2page_file
   # Each rst page name has a corresponding input file and mapping from
   # rst file line numbers to input file line numbers.
   page_name2line_tuple = dict()
   page_name2page_file  = dict()
   #
   # any_warning
   any_warning = [ False ]
   #
   # unknown_word_dict
   # Each key in this dict is a word not in dictionary or special words
   # The corresponding value is the number of pages it is an error for.
   unknown_word_dict = dict()
   #
   # group_name
   for group_name in group_list :
      #
      # old_group_name, new_group_name
      if rename_group == None :
         old_group_name = group_name
         new_group_name = group_name
      else :
         old_group_name = rename_group[0]
         new_group_name = rename_group[1]
         assert new_group_name == group_name
      #
      if new_group_name not in root_file :
         msg  = f'The group name {new_group_name} is '
         if rename_group == None :
            msg += 'in --group_list\n'
         else :
            msg += 'is new_group_name in --rename_group\n'
         msg += 'but it is not a valid key for the root_file table of\n'
         msg += f'the configuration file {config_file}'
         xrst.system_exit(msg)
      #
      if not os.path.isfile( root_file[new_group_name] ) :
         file_name = root_file[new_group_name]
         msg  = f'The root_file for group_name {new_group_name} is not a file\n'
         msg += f'file name = {file_name}'
         xrst.system_exit(msg)
      #
      # finfo_stack, finfo_done
      # This information is by file, not page
      finfo_stack      = list()
      finfo_done       = list()
      finfo = {
         'file_in'        : root_file[new_group_name],
         'parent_file'    : None,
         'parent_page'    : None,
      }
      finfo_stack.append(finfo)
      #
      while 0 < len(finfo_stack) :
         #
         # finfo
         # pop first element of stack so that order in tex file and
         # table of contents is correct
         finfo  = finfo_stack.pop(0)
         #
         for finfo_tmp in finfo_done :
            if finfo_tmp['file_in'] == finfo['file_in'] :
               msg  = 'The file ' + finfo['file_in']
               msg += '\nis included twice with '
               msg += f'group_name = "{old_group_name}"\n'
               msg += 'Once in ' + finfo_tmp['parent_file'] + '\n'
               msg += 'and again in ' + finfo['parent_file'] + '\n'
               xrst.system_exit(msg)
         finfo_done.append(finfo)
         #
         file_in              = finfo['file_in']
         parent_file          = finfo['parent_file']
         parent_file_page  = finfo['parent_page']
         assert os.path.isfile(file_in)
         #
         # get xrst documentation in this file
         file_page_info = xrst.get_file_info(
            all_page_info,
            old_group_name,
            parent_file,
            file_in,
         )
         #
         # root_page_list
         if finfo['parent_file'] == None :
            assert file_in == root_file[new_group_name]
            if file_page_info[0]['is_parent'] :
               n_page = 1
            else :
               n_page = len( file_page_info )
            for i_page in range( n_page ) :
               page_name = file_page_info[i_page]['page_name']
               root_page_list.append(page_name)
         #
         # parent_page_file_in
         # index in all_page_info of parent page for this file
         parent_page_file_in = None
         if file_page_info[0]['is_parent'] :
            parent_page_file_in = len(all_page_info)
         #
         # add this files pages to all_page_info
         for i_page in range( len(file_page_info) ) :
            # ------------------------------------------------------------
            # page_name, page_data, is_parent, begin_line
            page_name  = file_page_info[i_page]['page_name']
            page_data  = file_page_info[i_page]['page_data']
            is_parent  = file_page_info[i_page]['is_parent']
            begin_line = file_page_info[i_page]['begin_line']
            #
            # parent_page
            if is_parent or parent_page_file_in is None :
               parent_page = parent_file_page
            else :
               parent_page = parent_page_file_in
            #
            # all_page_info
            all_page_info.append( {
               'page_name'      : page_name,
               'file_in'        : file_in,
               'parent_page'    : parent_page,
               'begin_line'     : begin_line,
               'in_parent_file' : file_page_info[i_page]['is_child'],
               'end_line'       : file_page_info[i_page]['end_line'],
               'template_list'  : file_page_info[i_page]['template_list'],
            } )
            # ------------------------------------------------------------
            # template command
            # must come before almost all other commands; see its documentation
            page_data = xrst.template_command(page_data, file_in, page_name)
            # -------------------------------------------------------------
            # ref commands
            # Do this before spell checking so spell checking does not have
            # to deal with newlines in ref roles.
            page_data = xrst.ref_command(page_data)
            # -------------------------------------------------------------
            # comment_command
            page_data = xrst.comment_command(page_data)
            # -------------------------------------------------------------
            # spell_command
            # do after suspend and before other commands to help ignore
            # sections of text that do not need spell checking
            #
            # page_data, any_warning, unknown_word_dict
            page_data, spell_warning, unknown_word_set = xrst.spell_command(
               tmp_dir         = tmp_dir ,
               data_in         = page_data,
               page_file       = file_in,
               page_name       = page_name,
               begin_line      = begin_line,
               ignore_commands = ignore_spell_commands,
               print_warning   = not suppress_spell_warnings,
               spell_checker   = spell_checker,
            )
            if spell_warning :
               assert not suppress_spell_warnings
               any_warning[0] = True
            for word in unknown_word_set :
               if word in unknown_word_dict :
                  unknown_word_dict[word] += 1
               else :
                  unknown_word_dict[word] = 1
            # -------------------------------------------------------------
            # dir commands
            page_data = xrst.dir_command(page_data, rst2project_directory)
            # -------------------------------------------------------------
            # toc commands
            # page_data, finfo_stack, child_page_list, order
            page_data, child_file, child_page_list, order = \
               xrst.toc_commands(
                  is_parent,
                  page_data,
                  file_in,
                  page_name,
                  old_group_name,
            )
            #
            # all_page_info
            all_page_info[-1]['child_order'] = order
            #
            # page_index, finfo_stack
            page_index = len(all_page_info) - 1
            for file_tmp in child_file :
               finfo_stack.append( {
                  'file_in'        : file_tmp,
                  'parent_file'    : file_in,
                  'parent_page'    : page_index,
               } )
            # ------------------------------------------------------------
            # code commands
            page_data = xrst.code_command(
               page_data,
               file_in,
               page_name,
               rst2project_directory,
            )
            # ------------------------------------------------------------
            # literal command
            page_data = xrst.literal_command(
               page_data,
               file_in,
               page_name,
               rst2project_directory,
            )
            # ------------------------------------------------------------
            # process headings
            # pseudo_heading, page_title, keywords
            #
            check_headings = True
            xrst.process_headings(
               check_headings,
               conf_dict,
               local_toc,
               page_data,
               file_in,
               page_name,
               not_in_index_list,
            )
            check_headings = False
            page_data, page_title, pseudo_heading, keywords = \
            xrst.process_headings(
               check_headings,
               conf_dict,
               local_toc,
               page_data,
               file_in,
               page_name,
               not_in_index_list,
            )
            #
            # all_page_info
            # page title is used by table_of_contents
            all_page_info[page_index]['page_title']  = page_title
            all_page_info[page_index]['keywords']    = keywords
            # -------------------------------------------------------------
            # list_children
            # page_name for each of the children of the current page
            if not is_parent :
               list_children = child_page_list
            else :
               assert order in [ 'before', 'after' ]
               list_children = list()
               for i in range( len(file_page_info) ) :
                  if i != i_page :
                     list_children.append(
                        file_page_info[i]['page_name']
                     )
               if order == 'before' :
                  list_children = child_page_list + list_children
               else :
                  list_children = list_children + child_page_list
            # -------------------------------------------------------------
            # process children
            # want this as late as possible so toctree at end of input
            page_data = xrst.process_children(
               page_name,
               page_data,
               list_children,
            )
            # -------------------------------------------------------------
            #
            # line_tuple and file tmp_dir/page_name.rst
            line_tuple = xrst.temporary_file(
               page_source,
               target,
               pseudo_heading,
               file_in,
               tmp_dir,
               page_name,
               page_data,
            )
            #
            # page_name2line_tuple, page_name2page_file
            page_name2line_tuple[page_name] = line_tuple
            page_name2page_file[page_name]  = file_in
      #
      # check_input_files
      if rename_group == None :
         toc_file_set = set()
         for finfo_tmp in finfo_done :
            toc_file_set.add( finfo_tmp['file_in'] )
         input_file_list, file_list_warning = xrst.check_input_files(
            config_file, conf_dict, group_name, toc_file_set, input_file_list
         )
         if file_list_warning :
            any_warning[0] = True
   #
   # index_page_name
   ok = index_page_name == 'xrst_root_doc' or target == 'tex'
   for page_info in all_page_info :
      ok = ok or page_info['page_name'] == index_page_name
   if not ok :
      msg = f'index_page_name = {index_page_name} is not a valid page name.'
      xrst.system_exit(msg)
   #
   # rename_group
   if rename_group != None :
      xrst.rename_group(tmp_dir, rename_group[0], rename_group[1])
      #
      # tmp_dir
      # reset tmp_dir because rmtree is such a dangerous command
      tmp_dir = f'{rst_directory}/tmp'
      shutil.rmtree(tmp_dir)
      print('xrst --rename_group: OK')
      return
   #
   # replace_spell_commands
   if replace_spell_commands :
      xrst.replace_spell(tmp_dir)
      #
      # tmp_dir
      # reset tmp_dir because rmtree is such a dangerous command
      tmp_dir = f'{rst_directory}/tmp'
      shutil.rmtree(tmp_dir)
      print('xrst --replace_spell_commands: OK')
      return
   #
   # unknown_word_dict
   if not suppress_spell_warnings and len(unknown_word_dict) > 0 :
      assert any_warning[0] == True
      msg  = '\nBelow is a list of (word, count) pairs.\n'
      msg += 'Fix low count words using the spell command.\n'
      msg += 'Consider adding high count words to the project dictionary.\n'
      msg += 'If there are a lot of words and they are all correct,\n'
      msg += 'or a lot of word that are not needed (see above),\n'
      msg += 'consider using --replace_spell_commands.\n'
      sys.stderr.write(msg)
      unknown_word_list = sorted(
         unknown_word_dict.items(), key = lambda pair: pair[1]
      )
      line = ''
      for pair in unknown_word_list :
         pair_str = str(pair)
         if len(line) == 0 :
            line = pair_str
         elif len(line + pair_str) > 80 :
            sys.stderr.write(line + '\n')
            line = pair_str
         else :
            line += ' ' + pair_str
      if len(line) > 0 :
         sys.stderr.write(line + '\n')
      sys.stderr.write('\n')
   #
   # ignore_spell_commands
   if ignore_spell_commands :
      return
   #
   # auto_file
   xrst.auto_file(
      conf_dict      = conf_dict,
      link_timeout   = link_timeout,
      html_theme     = html_theme,
      target         = target,
      all_page_info  = all_page_info,
      root_page_list = root_page_list
   )
   #
   # not_rst_list
   not_rst_list = [ 'conf.py' , 'xrst_search.js' ]
   # -------------------------------------------------------------------------
   #
   # rst_directory/*.rst
   tmp_list = os.listdir(tmp_dir)
   rst_list = os.listdir(rst_directory)
   for name in tmp_list :
      src = f'{tmp_dir}/{name}'
      des = f'{rst_directory}/{name}'
      if name.endswith('.rst') or name in not_rst_list :
         if name not in rst_list :
               shutil.copyfile(src, des)
         else :
            if not filecmp.cmp(src, des, shallow=False) :
               os.replace(src, des)
   for name in rst_list :
      if name.endswith('.rst') :
         if name not in tmp_list :
            os.remove( f'{rst_directory}/{name}' )
   #
   # tmp_dir
   # reset tmp_dir because rmtree is such a dangerous command
   tmp_dir = f'{rst_directory}/tmp'
   shutil.rmtree(tmp_dir)
   # -------------------------------------------------------------------------
   if rst_only :
      print('xrst rst_only: OK')
      indent = '\n' + 3 * ' '
      txt = ''
      if external_links :
         txt  = f'The following command will check the external links'
         txt += indent
         txt += f'sphinx-build -b linkcheck -j {number_jobs} '
         txt += f'{rst_directory} {target_directory}'
         txt += '\n\n'
      if target == 'html' :
         txt += f'The following commands will build the html:'
         txt += indent
         txt += f'sphinx-build -b html -j {number_jobs} '
         txt += f'{rst_directory} {target_directory}'
         txt += indent
         txt += f'rm -r {target_directory}/_sources'
         txt += indent
         txt += f'mv {rst_directory}/_sources {target_directory}/_sources'
         if html_theme == 'sphinx_rtd_theme' :
            txt += '\nThis will not modify the sphinx_rtd_theme maximum width'
      else :
         assert target == 'tex'
         latex_dir = f'{target_directory}'
         txt += f'The following command will build the tex:'
         txt += indent
         txt += f'sphinx-build -b latex -j {number_jobs} '
         txt += f'{rst_directory} {latex_dir}'
         txt += '\n'
         txt += f'The following command will build the pdf from the tex:'
         txt += indent
         txt += f'make -C {project_directory}/{latex_dir} {project_name}.pdf'
      print(txt)
      return
   #
   # -------------------------------------------------------------------------
   if external_links :
      command  = f'sphinx-build -b linkcheck -j {number_jobs} '
      command += f'{rst_directory} {target_directory}'
      if rst_line_numbers :
         system_command(command, any_warning)
      else :
         system_command(
            command, any_warning, page_name2line_tuple, page_name2page_file
      )
   if target == 'html' :
      command  = f'sphinx-build -b html -j {number_jobs} '
      command += f'{rst_directory} {target_directory}'
      if rst_line_numbers :
         system_command(command, any_warning)
      else :
         system_command(
            command, any_warning, page_name2line_tuple, page_name2page_file
         )
         #
         # target_directory/_sources
         # replace sphinx _sources directory with proper xrst sources
         if not rst_line_numbers :
            src_dir = f'{rst_directory}/_sources'
            des_dir = f'{target_directory}/_sources'
            print( f'rm -r {des_dir}' )
            shutil.rmtree(des_dir)
            print( f'cp -r {src_dir} {des_dir}' )
            shutil.copytree(src_dir, des_dir)
         #
         # target_directory/index.html
         src_file = f'{target_directory}/{index_page_name}.html'
         des_file = f'{target_directory}/index.html'
         shutil.copyfile(src_file, des_file)
         #
         # target_directory/xrst_search.js
         src_file = f'{rst_directory}/xrst_search.js'
         des_file = f'{target_directory}/xrst_search.js'
         shutil.copyfile(src_file, des_file)
         #
   else :
      assert target == 'tex'
      #
      latex_dir = f'{target_directory}'
      command  = f'sphinx-build -b latex -j {number_jobs} '
      command += f'{rst_directory} {latex_dir}'
      if rst_line_numbers :
         system_command(command, any_warning)
      else :
         system_command(
            command, any_warning, page_name2line_tuple, page_name2page_file
         )
      #
      # latex_dir/project_name.tex
      fix_latex(latex_dir, project_name)
      #
      print('The following command will build the pdf from the latex:')
      print( f'   make -C {project_directory}/{latex_dir} {project_name}.pdf' )
   # -------------------------------------------------------------------------
   # target_directory/_static/css/theme.css
   # see https://stackoverflow.com/questions/23211695/
   #  modifying-content-width-of-the-sphinx-theme-read-the-docs
   if html_theme == 'sphinx_rtd_theme' and target == 'html' :
      pattern = dict()
      pattern['content'] = re.compile(
         r'([.]wy-nav-content[{][^}]*;max-width):[^;]*;'
      )
      pattern['sidebar'] = re.compile(
         r'([.]wy-nav-side[{][^}]*;width):[^;]*;'
      )
      pattern['search'] = re.compile(
         r'([.]wy-side-nav-search[{][^}]*;width):[^;]*;'
      )
      new_value = { 'content':'100%', 'sidebar':'250px', 'search':'250px' }
      file_name = f'{target_directory}/_static/css/theme.css'
      if os.path.exists(file_name + '.bak' ) :
        shutil.copyfile(file_name + '.bak', file_name)
      else :
        shutil.copyfile(file_name, file_name + '.bak')
      try :
         file_obj  = open(file_name, 'r')
         ok        = True
      except :
         ok        = False
      if ok :
         data_in   = file_obj.read()
         file_obj.close()
         match     = dict()
         for key in pattern :
            match[key] = pattern[key].search(data_in)
            ok         = match[key] != None
      if ok :
         for key in pattern :
            match[key] = pattern[key].search(data_in, match[key].end())
            ok        = match[key] == None
      if ok :
         data_out = data_in
         for key in pattern :
            data_tmp  = data_out
            value     = new_value[key]
            data_out  = pattern[key].sub( f'\\1:{value};', data_tmp)
            ok        = data_out != data_tmp
      if not ok :
         msg       = 'warning: cannot modify widths in sphinx_rtd_theme\n'
         sys.stderr.write(msg)
         any_warning[0] = True
      else :
         file_obj  = open(file_name, 'w')
         file_obj.write(data_out)
         file_obj.close()
   # -------------------------------------------------------------------------
   if any_warning[0] and not continue_with_warnings :
      system_exit('xrst: See warnings above')
   else :
      print('xrst: OK')
