# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: Bradley M. Bell <bradbell@seanet.com>
# SPDX-FileContributor: 2020-25 Bradley M. Bell
# ----------------------------------------------------------------------------
import re
# {xrst_begin xrst.pattern dev}
# {xrst_spell
# }
# {xrst_comment_ch #}
#
# The xrst.pattern Dictionary
# ###########################
#
# pattern
# *******
# This dictionary contains compiled regular expressions.
# It does not change after its initial setting when this file is imported.
# {xrst_code py}
pattern = dict()
# {xrst_code}
#
# begin
# *****
# Pattern for the begin command.
#
# 0. preceding character or empty + the command.
# 1. preceding character or empty
# 2. begin or begin_parent
# 3. the page name (without leading or trailing spaces or tabs)
# 4. the group name (with leading and trailing spaces and tabs)
#
# {xrst_code py}
pattern['begin'] = re.compile(
   r'(^|[^\\])\{xrst_(begin|begin_parent)[ \t]+([^ \t}]*)([^}]*)}'
)
# {xrst_code}
#
# code
# ****
# Pattern for code command.
#
# 0. the entire line for the command with newline at front.
# 1. the indent for the command (spaces and tabs)
# 2. is the command with or without characters in front
# 3. This is the non space characters after the indent and before
#    command (or None)
# 4. the language argument which is empty (just white space)
#    for the second code command in each pair.
# 5. the line number for this line; see pattern['line'] above.
#
# {xrst_code py}
pattern['code'] = re.compile(
   r'\n([ \t]*)(\{xrst_code *|([^\n]*[^\n\\])\{xrst_code *)' +
   r'([^@]*)}[^\n]*@xrst_line ([0-9]+)@'
)
# {xrst_code}
#
# comment_ch
# **********
# Pattern for comment_ch command
#
# 1. empty or character before command + the command
# 2. is the character (matched as any number of not space, tab or }
#
# {xrst_code py}
pattern['comment_ch'] = re.compile(
   r'(^|[^\\])\{xrst_comment_ch\s+([^} \t]*)\s*}'
)
# {xrst_code}
#
# dir
# ***
# Pattern for dir command
#
# 1. Is either empty of character before command
# 2. Is the file_name in the command
#
# {xrst_code py}
# pattern_dir
pattern['dir'] = re.compile(
   r'(^|[^\\]){xrst_dir[ \t]+([^}]*)}'
)
# {xrst_code}
#
# end
# ***
# Pattern for end command
#
# 0. preceding character + white space + the command.
# 1. the page name.
#
# {xrst_code py}
pattern['end'] = re.compile( r'[^\\]\{xrst_end\s+([^}]*)}' )
# {xrst_code}
#
#
# line
# ****
# Pattern for line numbers are added to the input by add_line_number
#
# 0. the line command.
# 1. the line_number.
#
# {xrst_code py}
pattern['line'] = re.compile( r'@xrst_line ([0-9]+)@' )
# {xrst_code}
#
# literal
# *******
# Pattern for the literal command. Groups 1 and 2 will be None for this
# pattern if \{xrst_literal} is matched.
#
# 0. preceding character + the command.
# 1. characters, not including line number or command name, on first line.
# 2. rest of command, not including first \\n or final }.
#
# {xrst_code py}
pattern['literal'] = re.compile(
r'[^\\]\{xrst_literal([^\n}]*)@xrst_line [0-9]+@\n([^}]*)}|[^\\]\{xrst_literal}'
)
# {xrst_code}
#
# template_begin
# **************
# 0. @\{xrst_template_begin@ *template_file* @ *page_line* @}
# 1. *template_file*
# 2. *page_line*
# {xrst_code py}
# Use \{xrst instead of {xrst so pattern does not look like template begin
pattern['template_begin']  = re.compile(
   r'@\{xrst_template_begin@([^@]*)@([^@]*)@}@'
)
# {xrst_code}
#
# template_end
# ************
# 0. @\{xrst_template_end@
# {xrst_code py}
# Use \{xrst instead of {xrst so pattern does not look like template end
pattern['template_end']    = re.compile( r'@\{xrst_template_end}@' )
# {xrst_code}
#
# toc
# ***
# Patterns for the toc_hidden, toc_list, and toc_table commands.
#
# 0. preceding character + the command.
# 1. command name; i.e., hidden, list, or table
# 2. the rest of the command that comes after the command name.
#    This is an option order (on same line) followed by
#    a list of file names with one name per line.
#    The } at the end of the command is not included.
#    This pattern may be empty.
#
# If you change this pattern, check pattern_toc in process_children.py
# {xrst_code py}
pattern['toc']   = re.compile(
   r'[^\\]\{xrst_toc_(hidden|list|table)([^}]*)}'
)
# {xrst_code}
#
# {xrst_end xrst.pattern}
