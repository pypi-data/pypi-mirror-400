# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: Bradley M. Bell <bradbell@seanet.com>
# SPDX-FileContributor: 2020-25 Bradley M. Bell
# ----------------------------------------------------------------------------
r"""
{xrst_begin suspend_cmd user}
{xrst_spell
   op
}

Suspend and Resume Commands
###########################

Syntax
******
- ``\{xrst_suspend}``
- ``\{xrst_suspend`` *boolean* ``}``
- ``\{xrst_suspend`` *left* *op* *right* ``}``
- ``\{xrst_resume}``

Discussion
**********
It is possible to suspend (resume) the xrst extraction and processing.
One begins (ends) the suspension with a line that only contains spaces,
tabs and a suspend command (resume command).
Each suspend command must have a corresponding resume command.

White Space
***********
Leading and trailing spaces in *boolean* , *left* , *op* , and *right*
are ignored.

boolean
*******
If the argument *boolean* is present, it must be true or false.
If is true, or not present, the section of input up to the next resume
is not included in the xrst extraction and processing for this page.
This argument is intended to be used by the
template command where it can be assigned the value true or false
for a particular expansion of the :ref:`template_cmd@template_file` .

*op*
****
This argument must be ``==`` or ``!=``.
It must be separated one or more spaces from *left* and *right* .

left, right
***********
If arguments *left* and *right* must not have any white space in them.
If

 *left* *op* *right*

is true (false) ,
the section of input up to the next resume
is not included in the xrst extraction and processing for this page.

Example
*******
:ref:`suspend_example-name`

{xrst_end suspend_cmd}
"""
# ----------------------------------------------------------------------------
import re
import xrst
#
# pattern_suspend, pattern_resume
pattern_suspend = re.compile(
   r'[^\\]{xrst_suspend *([^}]*)}'
)
pattern_resume  = re.compile(
   r'[^\\]{xrst_resume}'
)
# {xrst_begin suspend_cmd_dev dev}
# {xrst_comment_ch #}
#
# Remove text specified by suspend / resume pairs
# ###############################################
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
# is the data for this page.
#
# page_file
# *********
# is the :ref:`begin_cmd@Page File` for this page.
#
# page_name
# *********
# is the name of this page.
#
# data_out
# ********
# The return data_out is a copy of data_in except that the text between
# and including each suspend / resume pair has been removed.
#
# {xrst_end suspend_cmd_dev}
# BEGIN_DEF
def suspend_command(data_in, page_file, page_name) :
   assert type(data_in) == str
   assert type(page_file) == str
   assert type(page_name) == str
   # END_DEF
   #
   # data_out
   data_out = data_in
   #
   # m_suspend
   m_suspend  = pattern_suspend.search(data_out)
   while m_suspend != None :
      #
      # m_resume
      m_resume      = pattern_resume.search(data_out, m_suspend.end())
      if m_resume == None :
         msg  = 'There is a suspend command without a '
         msg += 'corresponding resume command.'
         xrst.system_exit(msg,
            file_name=page_file,
            page_name=page_name,
            m_obj=m_suspend,
            data=data_out
         )
      #
      # m_obj
      m_obj = pattern_suspend.search(data_out, m_suspend.end())
      if m_obj != None :
         if m_obj.start() < m_resume.end() :
            msg  = 'There are two suspend commands without a '
            msg += 'resume command between them.'
            xrst.system_exit(msg,
               file_name=page_file,
               page_name=page_name,
               m_obj=m_obj,
               data=data_out
            )
      #
      # exclude
      argument = m_suspend.group(1).strip(' ')
      if argument in [ '', 'true' ] :
         exclude = True
      elif argument == 'false' :
         exclude = False
      else :
         argument = argument.split()
         if len(argument) != 3 :
            msg  = 'suspend command argument is not empty, true, false or'
            msg += 'three string separated by white space.'
            xrst.system_exit(msg,
               file_name=page_file,
               page_name=page_name,
               m_obj=m_obj,
               data=data_out
            )
         left  = argument[0]
         op    = argument[1]
         right = argument[2]
         if op == '==' :
            exclude = left == right
         elif op == '!=' :
            exclude = left != right
         else :
            msg  = '{' + 'xrst_suspend left op right}: '
            msg += 'op is not == or !=.'
            xrst.system_exit(msg,
               file_name=page_file,
               page_name=page_name,
               m_obj=m_obj,
               data=data_out
            )
      #
      # data_out
      if exclude :
         data_tmp  = data_out[: m_suspend.start() + 1]
         data_tmp += data_out[m_resume.end() : ]
      else :
         data_tmp  = data_out[: m_suspend.start() + 1]
         data_tmp += data_out[m_suspend.end() : m_resume.start() + 1]
         data_tmp += data_out[m_resume.end() : ]
      data_out  = data_tmp
      #
      # m_suspend
      m_suspend = pattern_suspend.search(data_out)
   # BEGIN_RETURN
   #
   assert type(data_out) == str
   return data_out
   # END_RETURN
