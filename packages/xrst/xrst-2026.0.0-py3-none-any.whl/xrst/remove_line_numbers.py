# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: Bradley M. Bell <bradbell@seanet.com>
# SPDX-FileContributor: 2020-24 Bradley M. Bell
# ----------------------------------------------------------------------------
import re
import xrst
#
#
pattern_error = re.compile( r'@xrst_line *[0-9]+@[^\n]' )
# {xrst_begin remove_line_numbers dev}
# {xrst_spell
#     tuple
#     tuples
# }
# {xrst_comment_ch #}
#
# Remove the number numbers
# #########################
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
# is a string with line number markers added by :ref:`add_line_numbers-name` .
# These lines number markers have the form:
#
#     ``@xrst_line`` *line_number* ``@`` .
#
# data_out
# ********
# The return data_out is a copy of data_in with the
# line number markers removed.
#
#
# rst2xrst_list
# *************
# The second return rst2xrst_list is a list of tuples.
# Each tuple in the list has two or four elements.
#
# First Tuple Element
# ===================
# is the line number in *data_out* corresponding to a line number marker
# that was removed from *data_in* .
# The lines in *data_out*  still contain the ``{xrst@before_title}`` commands
# that were in *data_in*.
# These are not included in the line number could (because they are
# removed before writing its rst file).
#
# Second Tuple Element
# ====================
# The second tuple element is the line number in the file that contains
# the begin command for this page.
#
# Third Tuple Element
# ===================
# This element is present If the current line in *data_out* is
# part of a template expansion.
# In this case, the third element is the template file name.
#
# Fourth Tuple Element
# ====================
# This element is present If the current line in *data_out* is
# part of a template expansion.
# In this case, the fourth element is the line in the template file.
#
# FourthTuple Element
# ===================
# If the current line in data_out corresponds to a template file,
# this is the line number in the template file. Otherwise, it is None.
#
# {xrst_end remove_line_numbers}
# BEGIN_DEF
def remove_line_numbers(data_in) :
   assert type(data_in) == str
   # END_DEF
   #
   # m_error
   m_error = pattern_error.search(data_in)
   if m_error :
      start = max(m_error.start() - 50, 0)
      end   = min(m_error.end() + 50, len(data_in))
      msg   = 'Program error: Line number tracking is confused:\n'
      msg  += 'Text before the bad line number =\n'
      msg  +=  data_in[start : m_error.start()]
      msg  += '\n---------------------------------\n'
      msg  += 'Line number with no newline at end =\n'
      msg  += m_error.group(0)
      msg  += '\n---------------------------------\n'
      msg  += 'Text after the bad line number =\n'
      msg  +=  data_in[m_error.end() :  end]
      msg  += '\n--------------------------------\n'
      xrst.system_exit(msg)
   #
   # template_list
   template_list = list()
   for m_template_begin in xrst.pattern['template_begin'].finditer(data_in) :
      template_start = m_template_begin.start()
      template_file  = m_template_begin.group(1).strip()
      page_line      = int( m_template_begin.group(2) )
      m_template_end = \
         xrst.pattern['template_end'].search(data_in, template_start)
      template_end   = m_template_end.end()
      #
      template_list.append(
         (template_start, template_end, page_line, template_file)
      )
   #
   # template_index
   def template_index(m_line) :
      assert type(m_line) == re.Match
      #
      if len(template_list) == 0 :
         return None
      #
      # index
      index = 0
      template_end  = template_list[index][1]
      while template_end < m_line.start() :
         index += 1
         if index == len(template_list) :
            return None
         template_end = template_list[index][1]
      template_start = template_list[index][0]
      if template_start <= m_line.start() and m_line.start() <= template_end :
         return index
      #
      return None
   #
   # previous_end
   # index of the end of the previous match
   previous_end  = 0
   #
   # line_out
   # index of next line in data_out
   line_out  = 1
   #
   # data_out, rst2xrst_list
   data_out      = ''
   rst2xrst_list = list()
   #
   # data_out, rst2xrst_list
   for m_line in xrst.pattern['line'].finditer(data_in) :
      #
      # before
      # character from end of previous match to start of this match
      before = data_in[previous_end  : m_line.start() ]
      #
      # line_out
      line_out  += before.count('\n')
      line_out  -= before.count('{xrst@before_title}\n')
      #
      # page_line, template_file, template_line
      index = template_index(m_line)
      if index == None :
         page_line     = int( m_line.group(1) )
         template_file = None
         template_line = None
      else :
         page_line     = template_list[index][2]
         template_line = int( m_line.group(1) )
         template_file = template_list[index][3]
      #
      # rst2xrst_list
      if index == None :
         rst2xrst_list.append( (line_out, page_line) )
      else :
         rst2xrst_list.append(
            (line_out, page_line, template_file, template_line)
         )
      #
      # data_out
      data_out += before
      #
      # previous_end
      previous_end = m_line.end()
   #
   # data_out
   data_out += data_in[previous_end  :]
   #
   # BEGIN_RETURN
   #
   assert type(data_out) == str
   assert type(rst2xrst_list) == list
   if 0 < len(rst2xrst_list) :
      assert type(rst2xrst_list[0]) == tuple
      assert type(rst2xrst_list[0][0]) == int
      assert type(rst2xrst_list[0][1]) == int
   return data_out, rst2xrst_list
   # END_RETURN
