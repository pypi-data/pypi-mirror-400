# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: Bradley M. Bell <bradbell@seanet.com>
# SPDX-FileContributor: 2020-24 Bradley M. Bell
# ----------------------------------------------------------------------------
r"""
{xrst_begin auto_indent dev}

Automatic Indentation
#####################
Compute the indentation at the beginning of every line in *data* .
The characters that can be used to indent are spaces or tabs.
Lines that only have spaces and tabs are not included in this calculation.

Prototype
*********
{xrst_literal ,
   # BEGIN_DEF, # END_DEF
   # BEGIN_RETURN, # END_RETURN
}

data
****
is the data we are computing the indentation for.
The text before the first new_line does not matter.
If you want to include this text, add a newline at the beginning of *data*.

file_name
*********
used for error reporting when *data* mixes spaces and tabs in
the indentation.

page_name
*********
used for error reporting when *data* mixes spaces and tabs in
the indentation.

indentation
***********
The return value *indentation* is the automatically computed indentation.
It will be a sequence of spaces or tabs but it will not mix
spaces and tabs.

{xrst_end auto_indent}
"""
import re
import xrst
#
# pattern_newline
pattern_newline = re.compile( r'\n([ \t]*)[^ \t\n]' )
#
# BEGIN_DEF
def auto_indent(data, file_name, page_name) :
   assert type(data) == str
   assert type(file_name) == str
   assert type(page_name) == str
   # END_DEF
   #
   # len_data
   len_data   = len(data)
   #
   # newline_list
   newline_list = xrst.newline_indices(data)
   #
   # n_indent
   # use match_empty to gaurd against case where there are no matches
   n_indent    = len(data)
   m_itr       = pattern_newline.finditer(data)
   match_empty = True
   for m_obj in m_itr :
      match_empty = False
      n_indent    = min(n_indent, len( m_obj.group(1) ) )
   if match_empty :
      n_indent = 0
   #
   # check if there is no indent to remove
   if n_indent == 0 :
      return ''
   #
   # indent_ch
   line      = 0
   indent_ch = data[ newline_list[line] + 1 ]
   while indent_ch == '\n' :
      line += 1
      indent_ch = data[ newline_list[line] + 1 ]
   #
   # check for mixing spaces and tabs
   check_ch  = indent_ch + '\n'
   for newline in newline_list :
      next_ = newline + 1
      end   = min( len_data, next_ + n_indent )
      while next_ < end :
         if data[next_] not in check_ch :
            msg  = 'mixing both spaces and tabs for '
            msg += 'white space that indents this page.'
            xrst.system_exit(
               msg, file_name=file_name, page_name=page_name
            )
         next_ += 1
   #
   #
   # indentation
   indentation = n_indent * indent_ch
   #
   # BEGIN_RETURN
   assert type(indentation) == str
   return indentation
   # END_RETURN
