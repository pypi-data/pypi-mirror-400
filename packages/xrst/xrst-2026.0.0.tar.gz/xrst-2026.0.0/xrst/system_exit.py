# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: Bradley M. Bell <bradbell@seanet.com>
# SPDX-FileContributor: 2020-24 Bradley M. Bell
# ----------------------------------------------------------------------------
import sys
import os
import re
import xrst
#
# {xrst_begin system_exit dev}
# {xrst_spell
#     msg
# }
# {xrst_comment_ch #}
#
# Form error message and exit
# ###########################
#
# msg
# ***
# Reason for aborting xrst
#
# file_name
# *********
# is the name of the file that contains the begin command for this page.
# This is different from the current input file if we are processing
# a template expansion.
#
# page_name
# *********
# name of page that the error appeared in
#
# m_obj
# *****
# The error was detected in the values returned by this match object.
#
# data
# ****
# is the data that was searched to get the match object m_obj.
# If the error possibly occurred in a template expansion, you must include
# the entire expansion in the data.
#
# line
# ****
# is the line number in the current input file where the error
# was detected.
#
# Prototype
# *********
# {xrst_literal
#  # BEGIN_DEF
#  # END_DEF
#  }
#
# {xrst_end system_exit}
#
# BEGIN_DEF
def system_exit(
   msg, file_name=None, page_name=None, m_obj=None, data=None, line=None
) :
   assert type(msg)       == str
   assert type(file_name) == str or file_name == None
   assert type(page_name) == str or page_name == None
   assert type(line)  in [ int, str ] or line == None
   if m_obj != None :
      assert file_name != None
      assert data      != None
   # END_DEF
   #
   # extra
   project_directory = os.getcwd()
   extra          = f'\nproject_directory = {project_directory}\n'
   #
   # page_line, template_file, template_line
   page_line     = line
   template_file = None
   template_line = None
   if m_obj :
      page_line, template_file, template_line = xrst.file_line(m_obj, data)
   #
   # extra
   if page_name != None :
      extra += f'page = {page_name}\n'
   if file_name != None :
      extra += f'file = {file_name}\n'
   if page_line != None :
      extra += f'line = {page_line}\n'
   if template_file != None :
      extra += f'template_file = {template_file}\n'
      extra += f'template_line = {template_line}\n'
   #
   # breakpoint()
   sys.exit('xrst: Error\n' + msg + extra)
