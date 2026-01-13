# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: Bradley M. Bell <bradbell@seanet.com>
# SPDX-FileContributor: 2020-24 Bradley M. Bell
# ----------------------------------------------------------------------------
import sys
import os
import re
import xrst
# {xrst_begin file_line dev}
# {xrst_comment_ch #}
#
# Determine Input File and Line
# #############################
#
# {xrst_literal ,
#     # BEGIN_DEF ,    # END_DEF
#     # BEGIN_RETURN , # END_RETURN
# }
#
#
# m_obj
# *****
# is a match object for a location in data.
#
# data
# ****
# is the data for a page including template commands (or expansions
# if the templates commands have been processed).
#
# page_file
# *********
# This is the file where the begin and end commands appear for this page.
#
# page_line
# *********
# is the line number in the *page_file* corresponding to *m_obj*  .
# If *template_file* is None, *m_obj* starts at this line.
# Otherwise the template expansion for *template_file* starts at this line.
#
# template_file
# *************
# is the name of the file for the template expansion where the start of
# *m_obj* is located.  If *m_obj* does not start in a template expansion,
# *template_file* is None.
# In this case, *m_obj* starts in the file where the begin command for this
# page is located.
#
# template_line
# *************
# if *template_file* is None, *template_line* is None.
# Otherwise it is the line number in the *template_file* for this
# corresponding to this expansion.
#
# {xrst_end file_line}
# BEGIN_DEF
def file_line(m_obj, data) :
   assert type(m_obj) == re.Match
   assert type(data) == str
   # END_DEF
   #
   # match_line
   m_line  = xrst.pattern['line'].search( data[m_obj.start() :] )
   assert m_line != None
   match_line = int( m_line.group(1) )
   #
   #
   # template_expansion, begin_index
   begin_index = data[: m_obj.start()].rfind( '@{xrst_template_begin@' )
   end_index   = data[: m_obj.start()].rfind( '@{xrst_template_end}@' )
   template_expansion = end_index < begin_index
   #
   # page_line, template_file, template_line
   if not template_expansion :
      page_line      = match_line
      template_file  = None
      template_line  = None
   else :
      #
      # template_file, expansion_line
      m_temp = xrst.pattern['template_begin'].search( data[begin_index :] )
      assert m_temp != None
      template_file  = m_temp.group(1).strip()
      page_line      = int( m_temp.group(2) )
      template_line  = match_line
   # BEGIN_RETURN
   #
   assert type(page_line) == int
   if template_file == None :
      assert template_line == None
   else :
      assert type(template_file) == str
      assert type(template_line) == int
   return page_line, template_file, template_line
   # END_RETURN
