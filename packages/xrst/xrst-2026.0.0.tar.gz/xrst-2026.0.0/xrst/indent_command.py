# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: Bradley M. Bell <bradbell@seanet.com>
# SPDX-FileContributor: 2020-25 Bradley M. Bell
# ----------------------------------------------------------------------------
r"""
{xrst_begin indent_cmd user}

Indent Command
##############


Syntax
******
*indentation* ``\{xrst_indent}``

Discussion
**********
#. The xrst documentation for a page can be indented so that it is grouped
   with the source code it is next to.
#. We call lines that have just spaces or tabs empty lines
#. Empty lines below an indent command, and before the next indent command,
   must begin with *indent* . The indent characters
   are not included in the rst output; i.e., the indentation is removed.
#. If there is an indent command in a page,
   lines before the first indent command do not have any indentation.
#. If there is no indent command in a page,
   the indentation for the page is computed automatically.

indentation
***********
This is the sequence of spaces or a sequence of tabs that
come before ``\{xrst_indent}`` .
It cannot mix both spaces and tabs.

Automatic Indentation
*********************
If there is no indent command in a page,
the indentation is calculated automatically as follows:
The number of spaces (or tabs) before
all of the xrst documentation for a page
(not counting lines with just spaces or tabs)
is used for the indentation for that page.

Comment Character
*****************
The indentation is calculated before processing the
:ref:`comment_ch_cmd-name` command.

Example
*******
:ref:`indent_example-name`,
:ref:`comment_ch_example@Indent`, and
:ref:`example_ad_double@xrst_indent` .

{xrst_end indent_cmd}
"""
import re
import xrst
# {xrst_begin indent_cmd_dev dev}
# {xrst_comment_ch #}
#
# Process indent commands in a page
# #################################
#
# Prototype
# *********
# {xrst_literal ,
#  # BEGIN_DEF, # END_DEF
#  # BEGIN_RETURN, # END_RETURN
# }
#
# data_in
# *******
# is the data for this page.
#
# file_name
# *********
# is the input that this page appears in (used for error reporting).
#
# page_name
# *********
# is the name of this page (used for error reporting).
#
# data_out
# ********
# is a copy of data_in with the indentation for this section removed.
#
# {xrst_end indent_cmd_dev}
#

# pattern_indent
# 0. newline, characters before command, command
# 1. indent; i.e. , characters on same line and before the command.
pattern_indent = re.compile(
   r'\n{xrst_indent}|\n([^\n{]*[^\n\\]){xrst_indent}'
)
#
# pattern_newline
pattern_newline = re.compile( r'\n([ \t]*)[^ \t\n]' )
#
# pattern_space_or_tab
pattern_space_or_tab = re.compile( r'[ \n]*' )
#
# BEGIN_DEF
def indent_command(data_in, file_name, page_name) :
   assert type(data_in) == str
   assert type(file_name) == str
   assert type(page_name) == str
   # END_DEF
   #
   # data_out
   data_out = data_in
   #
   # m_obj
   m_obj = pattern_indent.search(data_out)
   if m_obj == None :
      #
      # indentation
      indentation = xrst.auto_indent(data_in, file_name, page_name)
      #
      # data_out
      pattern  = re.compile( r'\n' + indentation )
      data_out = pattern.sub('\n', data_out )
   else:
      #
      # m_obj
      while m_obj != None :
         #
         # indentation
         indentation = m_obj.group(1)
         if indentation == None :
            indentation = ''
         if pattern_space_or_tab.fullmatch(indentation) == None :
            msg  = f'indentation before {xrst_indent} = "'
            msg += indent + '"\n'
            msg += 'has characters that are not spaces or tabs'
            xrst.system_exit(msg,
               file_name = file_name,
               page_name = page_name,
               m_obj     = m_obj,
               data      = data_out
            )
         if '\n' in indentation and ' ' in indentation :
            msg = 'indentation before {xrst_indent} has spaces and tabs'
            xrst.system_exit(msg,
               file_name = file_name,
               page_name = page_name,
               m_obj     = m_obj,
               data      = data_out
            )
         #
         # this_start, this_end
         this_start  = m_obj.start()
         this_end    = m_obj.end()
         #
         # next_start, next_end
         m_next = pattern_indent.search(data_out, m_obj.end())
         if m_next == None :
            next_start = len(data_out)
         else :
            next_start = m_next.start()
         #
         # data_before, data_middle, data_after
         # include first match character (newline) in data_before
         data_before = data_out[: this_start + 1]
         data_middle = data_out[this_end : next_start]
         data_after  = data_out[next_start :]
         #
         # m_check
         for m_check in pattern_newline.finditer(data_middle) :
            if not m_check.group(1).startswith(indentation) :
               found = m_check.group(1)
               msg  = 'line does not begin with indentation '
               msg +='in previous indent command\n'
               msg += f'expected = "{indentation}"\n'
               msg += f'found    = "{found}"'
               xrst.system_exit(msg,
                  file_name = file_name,
                  page_name = page_name,
                  m_obj     = m_check,
                  data      = data_middle
               )
         #
         # data_middle
         pattern     = re.compile( r'\n' + indentation )
         data_middle = pattern.sub('\n', data_middle)
         #
         # data_left, data_out
         data_left = data_before + data_middle
         data_out  = data_left + data_after
         #
         # m_obj
         m_obj = pattern_indent.search(data_out, len(data_left) )
   #
   # BEGIN_RETURN
   #
   assert type(data_out) == str
   return data_out
   # END_RETURN
