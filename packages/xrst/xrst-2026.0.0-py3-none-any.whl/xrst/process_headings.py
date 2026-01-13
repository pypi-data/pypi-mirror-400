# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: Bradley M. Bell <bradbell@seanet.com>
# SPDX-FileContributor: 2020-25 Bradley M. Bell
# ----------------------------------------------------------------------------
r"""
{xrst_begin heading_links user}

Heading Cross Reference Links
#############################

Index
*****
For each word in a heading,
a link is included in the index from the word to the heading.
In addition, each word is added to the html keyword meta data
next to the page heading.

Labels
******
A cross reference label is defined for linking
from anywhere to a heading. The details of how to use
these labels are described below.

Level Zero
==========
Each :ref:`page<begin_cmd@page>` can have only one header at
the first level which is a title for the page.

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

page_title
----------
The input below will display the page title as the linking text:

    ``:ref:`` \` *page_name* ``-title`` \`

Linking Text
------------
You can also explicitly choose the linking text using:

   ``:ref:`` \` *linking_text* ``<`` *page_name* ``-name>`` \`


Other Levels
============
The label for linking a heading that is not at level zero is the label
for the heading directly above it plus an at sign character :code:`@`,
plus the conversion for this heading.
These labels use the *page_name* for level zero,
without the ``-name`` or ``--title`` at the end.

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

Example
*******
:ref:`heading_example-name`

{xrst_end heading_links}
-------------------------------------------------------------------------------
"""
import re
import xrst
# -----------------------------------------------------------------------------
def check_anchor(
   label, m_label, data_out, page_file, page_name, previous_anchor
) :
   assert type(label) == str
   assert type(m_label) == re.Match
   assert type(data_out) == str
   assert type(page_file) == str
   assert type(previous_anchor) == dict
   #
   # anchor
   # convert to the following pattern: [a-z](-?[a-z0-9]+)*
   anchor = label.lower()
   anchor = re.sub( r'[^a-z0-9]', '-', anchor)
   anchor = re.sub( r'-+',        '-', anchor)
   anchor = re.sub( r'-$',        '',  anchor)
   anchor = re.sub( r'^[^a-z]*',  '',  anchor)
   if anchor == '' :
      msg  = 'The anchor corresponding to a header is empty.\n'
      msg += f'label = {label}'
      xrst.system_exit(msg,
         file_name = page_file,
         page_name = page_name,
         m_obj     = m_label,
         data      = data_out,
      )
   #
   # check for duplicate anchor
   if anchor in previous_anchor :
      m_previous = previous_anchor[anchor]['m_label']
      page_line, template_file, template_line = xrst.file_line(
         m_obj = m_previous, data = data_out
      )
      previous_label = previous_anchor[anchor]['label']
      msg  = 'A previous header has the same HTML anchor.\n'
      msg += f'anchor         = {anchor}\n'
      msg += f'label          = {label}\n'
      msg += f'previous label = {previous_label}\n'
      msg += f'previous file  = {page_file}\n'
      msg += f'previous line  = {page_line}'
      if template_file != None :
         msg += f'\nprevious template file  = {template_file}'
         msg += f'\nprevious template line  = {template_line}'
      xrst.system_exit(
         msg,
         file_name = page_file,
         page_name = page_name,
         m_obj     = m_label,
         data      = data_out,
      )
      assert False, msg
   #
   # previous_anchor
   previous_anchor[anchor] = { 'm_label' : m_label, 'label' : label }
# -----------------------------------------------------------------------------
# {xrst_begin process_headings dev}
# {xrst_spell
#     conf
#     fullmatch
# }
# {xrst_comment_ch #}
#
# Add labels and index entries for headings
# #########################################
#
# Prototype
# *********
# {xrst_literal ,
#    # BEGIN_DEF, # END_DEF
#    # BEGIN_RETURN, # END_RETURN
# }
#
# check_headings
# **************
# If *check* is true, an error in a headings or its corresponding label,
# will result in an error message and program exit.
# This should be True on the first call and false on the second.
# Two passes are required because *data_out* does not change on the
# first pass so that all the match objects can be used for error messaging.
#
# conf_dict
# *********
# is a python dictionary representation of the configuration file.
#
# local_toc
# *********
# is the xrst command line local_toc setting.
#
# data_in
# *******
# contains the data for a page before the headings are processed.
#
# page_file
# *********
# name of the file that contains the begin command for this page.
# This is only used for error reporting.
#
# page_name
# *********
# is the name of this page.
#
# not_in_index_list
# *****************
# is a list of compiled regular expressions. If pattern is in this list,
# *word* is a lower case version of a word in the heading text, and
# pattern.fullmatch( *word* ) returns a match, an index entry is not
# generated for word.
#
# data_out
# ********
# is a copy of data_in with the following extra command added:
#
#  #. The index entries, and meta keyword entries (same as index),
#     and the :ref:`heading_links@Labels` for this page.
#  #. The command \\n{xrst@before_title} is placed directly before the
#     first heading for this page; i.e. its title.
#     This is makes it easy to add the page number to the heading text.
#
# page_title
# **********
# This is the heading text in the first heading for this page.
# There can only be one heading at this level.
#
# pseudo_heading
# **************
# This is an automatically generated heading for this page. It is intended
# to come before the page_title heading.
# It has three lines each terminated by a newline:
#
#  1. an overline line
#  2. heading text line for this page title
#  3. an underline line
#
# keywords
# ********
# This is a space separated  list, of the lower case words,
# for all the words that are in the # title and the headings for this page.
# This is the same as the index words for this page minus the words that
# match *not_in_index_list* .
#
# {xrst_end process_headings}
# BEGIN_DEF
def process_headings(
      check_headings,
      conf_dict,
      local_toc,
      data_in,
      page_file,
      page_name,
      not_in_index_list
) :
   assert type(check_headings) == bool
   assert type(conf_dict) == dict
   assert type(local_toc) == bool
   assert type(data_in) == str
   assert type(page_file) == str
   assert type(page_name) == str
   assert type(not_in_index_list) == list
   # END_DEF
   #
   # data_out
   data_out = data_in
   #
   # headinge_character, heading_overline
   heading_character = conf_dict['heading']['character']
   heading_overline  = conf_dict['heading']['overline']
   #
   # check_heading_level
   def check_heading_level(m_line, level, character, overline) :
      if not level < len( heading_character ) :
         return
      ok =        character == heading_character[level]
      ok = ok and overline  == heading_overline[level]
      if not ok :
         msg  = f'This heading is at level {level} and its\n'
         msg +=  f'underline character is "{character}"'
         msg += f' and overline is {overline}\n'
         msg += 'In the config_file this level has\n'
         msg +=  'underline character "' + heading_character[level]
         msg += '" and overline = ' + str( heading_overline[level] ) + '\n'
         xrst.system_exit(
            msg,
            file_name = page_file,
            page_name = page_name,
            m_obj     = m_line,
            data      = data_out,
         )
   #
   # pattern_colon_in_label
   pattern_colon_space = re.compile( r':(\s)' )
   #
   if check_headings :
      #
      # external_label, internal_label
      m_external_label, m_internal_label = xrst.sphinx_label(
         data_in, page_file, page_name
      )
      external_line = dict()
      for label in m_external_label :
         external_line[label] = m_external_label[label].group(3)
      internal_line = dict()
      for label in m_internal_label :
         internal_line[label] = m_internal_label[label].group(3)
      #
      # previous_anchor
      previous_anchor = dict()
      for label in m_internal_label :
         m_label = m_internal_label[label]
         check_anchor(
            label = label,
            m_label         = m_label,
            data_out        = data_out,
            page_file       = page_file,
            page_name       = page_name,
            previous_anchor = previous_anchor,
         )
   #
   # punctuation
   punctuation      = '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'
   assert len(punctuation) == 34 - 2 # two escape sequences
   #
   # overline_used
   overline_used = set()
   #
   # found_level_one_heading
   found_level_one_heading = False
   #
   # keywords, heading_list, heading_index, heading_text, underline_text
   keywords         = ' '
   heading_list     = list()
   data_index       = 0
   heading_index, heading_text, underline_text = \
      xrst.next_heading(data_out, data_index, page_file, page_name)
   #
   while 0 <= heading_index :
      if 0 < heading_index :
         assert data_out[heading_index-1] == '\n'
      #
      # m_line
      m_line = xrst.pattern['line'].search(data_out, heading_index)
      #
      # overline
      index = m_line.start()
      overline = underline_text == data_out[heading_index : index]
      #
      # character
      character = underline_text[0]
      #
      # heading
      heading   = {
         'overline' : overline,
         'character': character,
         'text':      heading_text
      }
      #
      # underline_end
      underline_end = data_out.find('\n', heading_index)
      underline_end = data_out.find('\n', underline_end+1)
      if overline :
         underline_end = data_out.find('\n', underline_end+1)
      assert data_out[underline_end] == '\n'
      #
      # overline_used
      if overline :
         overline_used.add(character)
      #
      # heading_list
      if len( heading_list ) == 0 :
         # first heading in this page
         heading_list.append( heading )
      else :
         # level_zero
         level_zero = overline == heading_list[0]['overline']
         if level_zero :
            level_zero = character == heading_list[0]['character']
         if level_zero :
            msg = 'There are multiple titles for this page'
            assert check_headings, False
            xrst.system_exit(msg,
               file_name = page_file,
               page_name = page_name,
               m_obj     = m_line,
               data      = data_out,
            )
         #
         # found_level
         found_level = False
         level       = 1
         while level < len(heading_list) and not found_level :
            found_level = overline == heading_list[level]['overline']
            if found_level :
               found_level = character == heading_list[level]['character']
            if found_level :
               #
               # heading_list
               heading_list = heading_list[: level ]
               heading_list.append(heading)
            else :
               level += 1
         #
         # heading_list
         if not found_level :
            # this heading at a higher level
            heading_list.append( heading )
      #
      # check_heading_level
      check_heading_level(
         m_line    = m_line,
         level     = len( heading_list) - 1,
         character = character,
         overline  = overline,
      )
      #
      # label
      label = None
      for level in range( len(heading_list) ) :
         if level == 0 :
            assert page_name == page_name.replace('\\', '').replace('@', '_')
            #
            # label
            if len(heading_list) == 1 :
               label = page_name + '-title'
            else :
               label = page_name
         else :
            conversion  = heading_list[level]['text']
            conversion  = conversion.replace('\\', '')
            conversion  = conversion.replace('@',  '-')
            conversion  = pattern_colon_space.sub( '\\:\\1', conversion)
            label      += '@' + conversion
      #
      # label
      if label.endswith(':') :
         label = label[:-1] + '\\:'
      if label.startswith('_') :
         label = '\\' + label
      #
      # check external labels
      if check_headings :
         if label.lower() in m_external_label :
            m_label = m_external_label[ label.lower() ]
            page_line, template_file, template_line = xrst.file_line(
               m_obj = m_label, data = data_out
            )
            lower_case = label_lower()
            msg += '!!! Please report this as an xrst bug !!!!\n'
            msg  = 'The label for this heading has same lower case as another '
            msg += 'label in the same page:\n'
            msg += 'lower case = {lower_case}\n'
            msg += 'other file = {page_file}\n'
            msg += 'other line = {page_line}'
            if template_file != None :
               msg += '\nother template file = {template_file}'
               msg += '\nother template line = {template_line}'
            assert check_headings, False
            xrst.system_exit(msg,
               file_name = page_file,
               page_name = page_name,
               m_obj     = m_line,
               data      = data_out,
            )
         #
         # check_anchor
         check_anchor(
            label           = label,
            m_label         = m_line,
            data_out        = data_out,
            page_file       = page_file,
            page_name       = page_name,
            previous_anchor = previous_anchor
         )
      #
      # keywords, index_entries
      if len(heading_list) == 1 :
         index_entries = page_name
         #
         assert keywords == ' '
         keywords     += page_name + ' '
      else :
         index_entries = ''
      for word in heading_list[-1]['text'].lower().split() :
         #
         # keywords are for the entire page
         if keywords.find( f' {word} ' ) < 0 :
            keywords += word + ' '
         #
         # same index word can occur multiple places in a page.
         skip = False
         for pattern in not_in_index_list :
            m_obj = pattern.fullmatch(word)
            if m_obj :
               skip = True
         if not skip :
            if index_entries == '' :
               index_entries = word
            else :
               index_entries += ', ' + word
      #
      # data_tmp
      # data that comes before this heading
      data_tmp   = data_out[: heading_index]
      #
      # data_tmp
      # If first level one heading and sphinx_rtd_theme,
      # put jump table command before heading
      if len(heading_list) == 2 and not found_level_one_heading :
         found_level_one_heading = True
         if local_toc :
            data_tmp += '\n.. contents::\n'
            data_tmp += 3 * ' ' + ':local:\n\n'
      #
      # data_tmp
      # add sphnix index, and label commands
      cmd  = ''
      if index_entries != '' :
            cmd += '.. index:: '           + index_entries + '\n\n'
      cmd += '.. _' + label + ':\n\n'
      data_tmp  += cmd
      #
      # data_tmp
      # If level zero, put page number command just before heading
      if len(heading_list) == 1 :
         data_tmp += '{xrst@before_title}\n'
      #
      # data_tmp
      # add data from stat to end of heading
      assert data_out[underline_end] == '\n'
      data_tmp  += data_out[heading_index : underline_end]
      #
      # data_out
      data_right = data_out[underline_end : ]
      data_out   = data_tmp + data_right
      #
      # next heading
      data_index = len(data_tmp) + 1
      heading_index, heading_text, underline_text = \
         xrst.next_heading(data_out, data_index, page_file, page_name)
   #
   # keywords, data_out
   keywords = keywords.strip()
   if keywords != '' :
      cmd  = '.. meta::\n'
      cmd += 3 * ' ' + ':keywords: ' + keywords.replace(' ', ',') + '\n\n'
      data_out = cmd + data_out
   #
   if len(heading_list) == 0 :
      msg = 'There are no headings in this page'
      assert check_headings, False
      xrst.system_exit(msg, file_name = page_file, page_name=page_name)
   #
   # pseudo_heading
   i = 0
   while punctuation[i] in overline_used :
      i += 1
      if i == len(punctuation) :
         msg  = 'more than ' + len(punctuation) - 1
         msg += ' overlined heading levels'
         assert check_headings, False
         xrst.system_exit(
            msg, file_name = page_file, page_name=page_name
         )
   line           = len(page_name) * punctuation[i] + '\n'
   pseudo_heading = line + page_name + '\n' + line + '\n'
   #
   # page_title
   page_title = heading_list[0]['text']
   #
   # BEGIN_RETURN
   #
   if check_headings :
      return
   assert type(data_out) == str
   assert type(page_title) == str
   assert type(pseudo_heading) == str
   assert type(keywords) == str
   return data_out, page_title, pseudo_heading, keywords
   # END_RETURN
