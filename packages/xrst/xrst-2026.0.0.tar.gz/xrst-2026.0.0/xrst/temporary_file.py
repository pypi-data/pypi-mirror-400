# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: Bradley M. Bell <bradbell@seanet.com>
# SPDX-FileContributor: 2020-25 Bradley M. Bell
# ----------------------------------------------------------------------------
import re
import xrst
pattern_line_number     = re.compile(r'\n[ \t]*@xrst_line [0-9]+@')
pattern_newline_3       = re.compile(r'(\n[ \t]*){2,}\n')
pattern_white_at_eol    = re.compile(r'[ \t]*\n')
#
# PAGE_NAME_PATTERN = [A-Za-z0-9._-]+
# use git grep PAGE_NAME_PATTERN to get all occurrences of this pattern
pattern_ref_page_name_1 = re.compile(r':ref:`([A-Za-z0-9._-]+)-name`')
pattern_ref_page_name_2 = re.compile(
                           r':ref:`([^`<]*)<([A-Za-z0-9._-]+)-name>`'
)
pattern_any_command     = re.compile(r'[^\\]{xrst_([a-zA-Z_]*)')
# ----------------------------------------------------------------------------
# {xrst_begin temporary_file dev}
# {xrst_spell
#     tuple
# }
# {xrst_comment_ch #}
#
# Write the temporary RST file for a page
# #######################################
#
# Prototype
# *********
# {xrst_literal ,
#    # BEGIN_DEF, # END_DEF
#    # BEGIN_RETURN, # END_RETURN
# }
#
# page_source
# ***********
# If *page_source* is true and *target* is html,
# a link to the xrst source code is included at the
# top of each page.
# If *page_source* is true and *target* is tex,
# the location of the xrst source code is reported at the
# top of each page.
#
# target
# ******
# If the :ref:`run_xrst@target` command line argument.
#
# pseudo_heading
# **************
# is the :ref:`process_headings@pseudo_heading` for this page.
#
# file_in
# *******
# is the name of the xrst input file for this page.
#
# tmp_dir
# *******
# is the directory where the output file will be saved.
#
# page_name
# *********
# is the name of this page.
#
# file_out
# ********
# The temporary file written by the routine, *file_out* , is
# tmp_dir/page_name.rst.

# data_in
# *******
# is the data for this page with all the xrst commands converted to
# their sphinx RST values, except the \\n\{xrst\@before_title} command.
# The following is added to this data before writing it to the output file:
#
#  #. The preamble is included at the beginning.
#  #. If *target* is ``html`` :
#
#     #. The *page_name* ``-name`` label is added next.
#     #. The pseudo heading is added next.
#     #. The name of the input file *file_in* is added next.
#
#  #. If *target* is ``tex`` :
#     All cross references of the form :ref:\` *page_name* -name \` ,
#     are changed to :ref:\` *page_name* < *page_name* -title >\` .
#     Note that the page name will be added to the title when
#     :ref:`add_before_title-name` is called during
#     :ref:`table_of_contents-name` .
#
#  #. Check for an xrst command that was not recognized.
#  #. Any sequence of more than 2 lines
#     with only tabs or space are converted to 2 empty lines.
#  #. Empty lines at the end are removed
#  #. The xrst_line_number entries are removed.
#  #. The xrst_template_begin and xrst_template_end markers are removed.
#  #. The text ``\\{xrst_`` is replaced by ``\{xrst_`` .
#
# rst2xrst_list
# *************
# This is the value returned by ``temporary_file`` .
# For each *index*, *rst2xrst_list* [ *index* ] is the a tuple; see
# :ref:`remove_line_numbers@rst2xrst_list` .
#
# {xrst_end temporary_file}
# BEGIN_DEF
# rst2xrst_list =
def temporary_file(
   page_source,
   target,
   pseudo_heading,
   file_in,
   tmp_dir,
   page_name,
   data_in,
) :
   assert target == 'html' or target == 'tex'
   assert type(page_source) == bool
   assert type(pseudo_heading) == str
   assert type(file_in) == str
   assert type(page_name) == str
   assert type(data_in) == str
   # END_DEF
   #
   # punctuation
   # Headings uses repeated copies of one of these characters
   punctuation = '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'
   #
   # label
   # label that displays page name (which is text in pseudo heading)
   label = f'.. _{page_name}-name:\n\n'
   #
   # data_out
   if target == 'html' :
      before   = label
      before  += pseudo_heading
      if page_source :
         if page_name.endswith('.rst') :
            destination = f'_sources/{page_name}.txt'
         else :
            destination = f'_sources/{page_name}.rst.txt'
         raw_html  = '.. raw:: html\n\n' + 3 * ' '
         raw_html += f'<a href="{destination}">View page source</a>\n\n'
         before   += raw_html
      data_out  = before + data_in
   else :
      if page_source :
         new_text   = f'**xrst input file** : {file_in}\n\n'
         #
         index      = data_in.find('\n{xrst@before_title}')
         first_line = index + len('\n{xrst@before_title}')
         assert data_in[first_line] == '\n'
         second_line = data_in.find('\n', first_line + 1)
         third_line  = data_in.find('\n', second_line + 1)
         fourth_line = data_in.find('\n', third_line + 1)
         #
         line     = data_in[first_line + 1 : second_line]
         overline = line[0] * len(line) == line and line[0] in punctuation
         if overline :
            text_index = fourth_line + 1
         else :
            text_index = third_line + 1
         data_before = data_in[: text_index]
         data_after  = data_in[text_index :]
         data_out    = data_before + new_text + data_after
      else :
         data_out = data_in
      #
      data_out   = pattern_ref_page_name_1.sub(
         r':ref:`\1<\1-title>`' , data_out
      )
      data_out   = pattern_ref_page_name_2.sub(
         r':ref:`\1<\2-title>`' , data_out
      )
   #
   # m_obj
   m_obj = pattern_any_command.search( data_out )
   while m_obj != None :
      ok = m_obj.group(0) == '@{xrst_template_begin'
      ok = ok or m_obj.group(0) == '@{xrst_template_end'
      if not ok :
         cmd  = m_obj.group(1)
         msg  = f'This xrst {cmd} command was not recognized.\n'
         msg += 'Use \\{xrst_' + cmd + ' '
         msg += 'if this is not intented to be an xrst command.'
         xrst.system_exit(msg,
            file_name=file_in,
            page_name=page_name,
            m_obj=m_obj,
            data=data_out
         )
      m_obj = pattern_any_command.search( data_out , m_obj.end() )
   #
   # data_out
   # Convert three or more sequential emtpty lines to two empty lines.
   data_out = pattern_line_number.sub('\n', data_out)
   data_out = pattern_newline_3.sub('\n\n', data_out)
   #
   # data_out
   # remove empty lines at the end
   while data_out[-2 :] == '\n\n' :
      data_out = data_out[: -1]
   #
   # data_out
   # The last step removing line numbers. This is done last for two reasons:
   # 1. So mapping from output to input line number is correct.
   # 2. We are no longer able to give line numbers for errors after this.
   data_out, rst2xrst_list = xrst.remove_line_numbers(data_out)
   #
   # data_out
   # Need the template_begin and template_end while removing line numbers
   # so that rst2xrst_list contains the template file information.
   data_out = xrst.pattern['template_begin'].sub('', data_out)
   data_out = xrst.pattern['template_end'].sub('', data_out)
   #
   # data_out
   data_out = data_out.replace( r'\{xrst_', '{xrst_' )
   #
   # data_out
   # remove white space at end of each line
   data_out = pattern_white_at_eol.sub(r'\n', data_out)
   #
   # file_out
   if page_name.endswith('.rst') :
      file_out = tmp_dir + '/' + page_name
   else :
      file_out = tmp_dir + '/' + page_name + '.rst'
   file_obj = open(file_out, 'w')
   file_obj.write(data_out)
   file_obj.close()
   #
   # BEGIN_RETURN
   #
   assert type(rst2xrst_list) == list
   assert type( rst2xrst_list[0] ) == tuple
   assert len( rst2xrst_list[0] ) == 2 or len( rst2xrst_list[0] ) == 4
   assert type( rst2xrst_list[0][0] ) == int
   assert type( rst2xrst_list[0][1] ) == int
   return rst2xrst_list
   # END_RETURN
