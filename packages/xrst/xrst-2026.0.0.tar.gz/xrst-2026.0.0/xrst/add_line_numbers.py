# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: Bradley M. Bell <bradbell@seanet.com>
# SPDX-FileContributor: 2020-24 Bradley M. Bell
# ----------------------------------------------------------------------------
import re
import xrst
#
# indent_pattern
indent_pattern = re.compile( r'^\n[ \t]*' )
#
# line_number_pattern
line_number_pattern = xrst.pattern['line']
#
# {xrst_begin add_line_numbers dev}
# {xrst_comment_ch #}
#
# Add Line Numbers to File Data
# #############################
# Add line numbers to a string in a way that is useful for reporting errors
# (for modified versions of string) using line number in the original string.
#
# Prototype
# *********
# {xrst_literal ,
#    # BEGIN_DEF, # END_DEF
#    # BEGIN_RETURN, # END_RETURN
# }
#
# data_in
# *******
# The original string.  An empty line is a line with just spaces or tabs.
# line_number is the number of newlines before a line plus one; i.e.,
# the first line is number one.
#
# file_in
# *******
# is the file corresponding to data_in (used for error reporting).
#
# data_out
# ********
# The return data_out is a modified version of data_in. The text
#
#  | ``@xrst_line`` *line_number* ``@``
#
# is added at the end of each non-empty line.
# There is one space between ``@xrst_line`` and *line_number*.
# There is no space between *line_number* and ``@`` .
# Spaces and tabs in empty lines are removed (so they are truly empty).
#
# {xrst_end add_line_numbers}
# BEGIN_DEF
def add_line_numbers(data_in, file_in) :
   assert type(data_in) == str
   assert type(file_in) == str
   # END_DEF
   #
   # data_extend
   data_extend = data_in
   if data_extend[-1] != '\n' :
      data_extend += '\n'
   #
   # m_obj
   m_obj = line_number_pattern.search(data_in)
   if m_obj != None :
      line = data_in[: m_obj.start() ].count('\n') + 1
      msg  = 'It is an error for the following text to appear in xrst input:\n'
      msg += '@xrst_line<space><number>@\n'
      msg += 'where <space> is a single space '
      msg += 'and <number> is an integer'
      xrst.system_exit(msg,
         file_name = file_in,
         line      = line,
         m_obj     = m_obj,
         data      = data_in
      )
   #
   # newline_list, line_start
   newline_list = xrst.newline_indices(data_extend)
   if newline_list[0] == 0 :
      line_start = 2
      newline_list .pop(0)
   else :
      line_start = 1
   #
   # data_out, previous
   data_out     = ""
   previous     = 0
   #
   for i in range( len(newline_list) ) :
      #
      # current
      current = newline_list[i]
      assert previous < current
      #
      # line
      line = data_extend[previous : current]
      #
      # empty_line
      if previous == 0 :
         m_obj = indent_pattern.search( '\n' + line )
         empty_line = m_obj.end() == len(line) + 1
      else :
         m_obj = indent_pattern.search( line )
         empty_line = m_obj.end() == len(line)
      #
      # line
      if empty_line :
         line = '\n'
      else :
         line += '@xrst_line ' + str(i + line_start) + '@'
      #
      # data_out, previous
      data_out  += line
      previous = current
   #
   # data_out
   assert previous == len(data_extend) - 1
   data_out += '\n'
   #
   # BEGIN_RETURN
   #
   assert type(data_out) == str
   return data_out
   # END_RETURN
