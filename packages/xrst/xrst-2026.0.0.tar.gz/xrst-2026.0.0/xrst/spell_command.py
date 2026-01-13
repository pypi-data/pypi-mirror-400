# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: Bradley M. Bell <bradbell@seanet.com>
# SPDX-FileContributor: 2020-25 Bradley M. Bell
# ----------------------------------------------------------------------------
r"""
{xrst_begin spell_cmd user}
{xrst_spell
   abcd
   cpp
   index index
}

Spell Command
#############

Syntax
******
- ``\{xrst_spell`` *word_1* ...  *word_n* ``}``
- ``\{xrst_spell_off}``
- ``\{xrst_spell_on}``

The lines containing the ``{`` ( ``}`` ) character
must have nothing but white space before ( after )  it.

spell_off
*********
By default xrst does spell checking.
You can turn spell checking off using this command.

spell_on
********
If spell checking has been turned off,
you can turn it back on using this command.

spell
*****
You can specify special words to include as correct spelling for
this page using this command.

Words
*****
Each word, that is checked for spelling, is a sequence of letters.
Upper case letters start a new word (even when preceded by a letter).

Special Words
*************
In the syntax above, the special word list is

| *word_1* ... *word_n*

These words are considered correct spelling even though
they are not in the dictionary.
In the syntax above the special words are all in one line.
They could be on different lines which helps when displaying
the difference between  versions of the corresponding file.
Latex commands should not be in the special word list because
words that have a backslash directly before them
are not include in spell checking.

project_dictionary
******************
The list of words in the
:ref:`config_file@project_dictionary`
are considered correct spellings for all pages.
If multiple people are working on a project using different spell checkers,
the words that are correct in one spell checker and not another should
be included in the project_dictionary.

page_name
*********
For each of the following commands in a page, the words in *page_name*
are considered correct spelling for that page:

| |tab| ``\{xrst_begin``        *page_name* *group_name* ``}``
| |tab| ``\{xrst_begin_parent`` *page_name* *group_name* ``}``
| |tab| ``:ref:`` \` ...  *page_name*\ ``-name`` ... `
| |tab| ``:ref:`` \` ...  *page_name*\ ``-title`` ... `

Note that *group_name* can be empty which corresponds to the default group;
see :ref:`begin_cmd-name` .

Capital Letters
***************
The case of the first letter does not matter when checking spelling;
e.g., if ``abcd`` is *word_1* then ``Abcd`` will be considered a valid word.
Each capital letter starts a new word; e.g., `CamelCase` is considered to
be the two words 'camel' and 'case'.
Single letter words are always correct and not included in the
special word list; e.g., the word list entry ``CppAD`` is the same as ``Cpp``.

Double Words
************
It is considered an error to have only white space between two occurrences
of the same word. You can make an exception for this by entering
the same word twice (next to each other) in the special word list.

Double words errors occur in the output the user sees.
for example, the input:
::

   `python package index <https://pypi.org/>`_ index.

results in the double word 'index index' in the output the user sees; i.e.,
the following output:
`python package index <https://pypi.org/>`_ index.

Example
*******
:ref:`spell_example-name`

{xrst_end spell_cmd}
"""
# ---------------------------------------------------------------------------
import sys
import re
import xrst
#
# pattern
pattern = dict()
pattern['spell']     = re.compile(
   r'[^\\]{xrst_spell([^_a-z][^}]*)}' +
   r'([ \t]*@xrst_line ([0-9]+)@)?'
)
pattern['word_error'] = re.compile( r'[^A-Za-z \t\n]' )
#
# pattern
# global pattern values used by spell command
pattern['template']  = xrst.pattern['template_begin']
pattern['dir']       = xrst.pattern['dir']
pattern['toc']       = xrst.pattern['toc']
pattern['code']      = xrst.pattern['code']
pattern['line']      = xrst.pattern['line']
pattern['literal']   = xrst.pattern['literal']
#
# pattern
# local pattern values only used by spell command
pattern['directive']  = re.compile( r'\n[ ]*[.][.][ ]+[a-z-]+::' )
pattern['http']       = re.compile( r'(https|http)://[A-Za-z0-9_/.#-]*' )
pattern['ref_name_1'] = re.compile( r':ref:`([^\n<`]+)-name`' )
pattern['ref_name_2'] = re.compile( r':ref:`[^\n<`]*<([^\n>`]+)-name *>`' )
pattern['ref_1']      = re.compile( r':ref:`[^\n<`]+`' )
pattern['ref_2']      = re.compile( r':ref:`([^\n<`]+)<[^\n>`]+>`' )
pattern['url_1']      = re.compile( r'`<[^\n>`]+>`_' )
pattern['url_2']      = re.compile( r'`([^\n<`]+)<[^\n>`]+>`_' )
pattern['tex_begin']  = re.compile( r'(\\begin|\\end){[a-z]*}' )
#
# pattern['spell_on'], pattern['spell_off']
lin = r'[ \t]*@xrst_line ([0-9]+)@'
pattern['spell_on']  = re.compile( r'\n[ \t]*\{xrst_spell_on}' + lin )
pattern['spell_off'] = re.compile( r'\n[ \t]*\{xrst_spell_off}' + lin )
#
# pattern['word']
# The first choice is for line numbers which are not in original file.
# The second is characters that are not letters, white space, or backslash.
# These character separate double words so they are not an error.
# The third is for the actual words (plus a possible backlash at start).
pattern['word']  = re.compile(
   r'(@xrst_line [0-9]+@|[^A-Za-z\s\\]+|\\?[A-Za-z][a-z]+)'
)
#
# pattern['page_name_word']
# The pattern for a word in the page name.
pattern['page_name_word'] = re.compile( r'[A-Za-z][a-z]+' )
# -----------------------------------------------------------------------------
# {xrst_begin spell_cmd_dev dev}
# {xrst_comment_ch #}
#
# Process the spell command for a page
# ####################################
#
# Prototype
# *********
# {xrst_literal ,
#    # BEGIN_DEF, # END_DEF
#    # BEGIN_RETURN, # END_RETURN
# }
#
# tmp_dir
# *******
# The file :ref:`replace_spell@spell.toml`
# is written in the *tmp_dir* directory by the one page at a time
# by this function call.
#
# data_in
# *******
# is the data for this page before the spell commands are removed.
#
# page_file
# *********
# is the name of the file where the begin command for this page appears.
# This is used for error reporting and for creating spell.toml.
#
# page_name
# *********
# is the name of the page that this data is in. This is only used
# for error reporting and spell.toml.
#
# begin_line
# **********
# is the line number in *page_file* where the begin command for this page
# appears. This is only used for spell.toml.
#
# ignore_commands
# ***************
# If this is true (false), :ref:`run_xrst@ignore_spell_commands`
# was (was not) on the command line.
#
# print_warning
# *************
# if this is false, do not print the spelling warnings. Otherwise,
# a spelling warning is reported for each word (and double word) that is not
# in the spell_checker dictionary or the special word list. A word is two or
# more letter characters. If a word is directly preceded by a backslash,
# it is ignored (so that latex commands do not generate warnings).
#
# spell_checker
# *************
# Is a spell checking object used for error checking; see
# :ref:`get_spell_checker-name`.
#
# data_out
# ********
# is the data for this page after the spell command (if it exists)
# is removed.
#
# spell_warning
# *************
# is true if a spelling error occurred and a warning was printed.
# Otherwise, it is false.
#
# unknown_word_set
# ****************
# is a lower case version of the set of words that are not in the
# spell_checker dictionary or the special word list.
# It does not include double word errors.
#
# {xrst_end spell_cmd_dev}
# BEGIN_DEF
def spell_command(
   tmp_dir,
   data_in,
   page_file,
   page_name,
   begin_line,
   ignore_commands,
   print_warning,
   spell_checker
) :
   assert type(tmp_dir) == str
   assert type(data_in) == str
   assert type(page_file) == str
   assert type(page_name) == str
   assert type(begin_line) == int
   assert type(print_warning) == bool
   # END_DEF
   #
   # first_spell_warning
   first_spell_warning = True
   #
   # unknown_word_set
   unknown_word_set = set()
   #
   # m_spell
   m_spell       = pattern['spell'].search(data_in)
   #
   # data_out
   data_out = data_in
   #
   # special_list, data_out
   special_list = list()
   if m_spell != None :
      #
      # check for multiple spell commands in one page
      m_error  = pattern['spell'].search(data_in, m_spell.end() )
      if m_error :
         msg  = 'There are two spell xrst commands in this page'
         xrst.system_exit(
            msg,
            file_name=page_file,
            page_name=page_name,
            m_obj=m_error,
            data=data_in
         )
      #
      # word_list
      word_list = m_spell.group(1)
      word_list = pattern['line'].sub('', word_list)
      m_error   = pattern['word_error'].search(word_list)
      if m_error :
         m_line = pattern['line'].search( data_in[m_spell.start() :] )
         line   = int( m_line.group(1) )
         line  += word_list[: m_error.start() ].count('\n')
         ch         = word_list[m_error.start()]
         ascii_code = ord(ch)
         msg  = 'The word list in spell command contains a character\n'
         msg += 'that is not a letter or white space.\n'
         msg += f'ascii code = {ascii_code}, character = {ch}.'
         #
         # The spell command cannot be inside a template file so we can use
         # line number to report the error.
         xrst.system_exit(
            msg,
            file_name=page_file,
            page_name=page_name,
            line = line,
         )
      #
      # special_list
      for m_obj in pattern['word'].finditer( word_list ) :
         word_lower = m_obj.group(0).lower()
         if not word_lower.startswith('@xrst_line') :
            special_list.append( word_lower )
      #
      # remove spell command
      start    = m_spell.start()
      end      = m_spell.end()
      data_out = data_in[: start+1] + data_in[end :]
   #
   # special_list
   if ignore_commands :
      special_list = list()
   #
   # special_used, double_used
   special_used   = dict()
   double_used    = dict()
   previous_word  = ''
   for word_lower in special_list :
      if word_lower == previous_word :
         double_used[ word_lower ] = False
      else :
         special_used[ word_lower ] = False
      #
      previous_word = word_lower
   #
   # data_tmp
   # version of data_in with certain commands removed
   data_tmp = data_out
   #
   # data_tmp
   # remove \< and \>, pattern matching below does not have to worry about it
   data_tmp = data_tmp.replace( r'\<', ' ')
   data_tmp = data_tmp.replace( r'\>', ' ')
   #
   # page_name_word
   page_name_word = list()
   for m_word in pattern['page_name_word'].finditer(page_name) :
      word_lower = m_word.group(0).lower()
      page_name_word.append( word_lower )
   for m_tmp in pattern['ref_name_1'].finditer(data_tmp) :
      page_name_tmp = m_tmp.group(1)
      for m_word in pattern['page_name_word'].finditer(page_name_tmp) :
         word_lower = m_word.group(0).lower()
         page_name_word.append( word_lower )
   for m_tmp in pattern['ref_name_2'].finditer(data_tmp) :
      page_name_tmp = m_tmp.group(1)
      for m_word in pattern['page_name_word'].finditer(page_name_tmp) :
         word_lower = m_word.group(0).lower()
         page_name_word.append( word_lower )
   #
   # m_off
   m_off = pattern['spell_off'].search(data_tmp)
   while m_off :
      #
      # m_on
      m_on = pattern['spell_on'].search(data_tmp, m_off.end() )
      #
      #
      off = m_off.start()
      #
      # on
      if m_on == None :
         on = len( data_tmp )
         m_off = pattern['spell_off'].search(data_tmp, off)
         if m_off :
            msg  = 'There are two spell_off commands '
            msg += 'without a spell_on command between them'
            xrst.system_exit(
               msg,
               file_name=page_file,
               page_name=page_name,
               m_obj=m_off,
               data=data_tmp
            )
      else :
         on = m_on.end()
      #
      # data_tmp
      data_tmp = data_tmp[: off ] + data_tmp[on : ]
      #
      # m_off
      m_off = pattern['spell_off'].search(data_tmp, off)
   #
   m_on = pattern['spell_on'].search(data_tmp)
   if m_on :
      msg  = 'There is a spell_on command '
      msg += 'without a spell_off command before it'
      xrst.system_exit(
         msg,
         file_name=page_file,
         page_name=page_name,
         m_obj=m_on,
         data=data_tmp
      )
   #
   # data_tmp
   # This is for detection of double word errors because these words are
   # automatically in the special word list.
   m_ref = pattern['ref_name_1'].search(data_tmp)
   while m_ref != None :
      page_name_tmp  = m_ref.group(1)
      page_name_words = ' '
      for m_word in pattern['page_name_word'].finditer(page_name_tmp) :
         word_lower       = m_word.group(0).lower()
         if page_name_words.find( f' {word_lower} ' ) < 0 :
            page_name_words += word_lower + ' '
      before   = data_tmp[: m_ref.start() ]
      after    = data_tmp[m_ref.end() :]
      data_tmp = before + ' ' + page_name_words + ' ' + after
      m_ref = pattern['ref_name_1'].search(data_tmp)
   #
   # data_tmp
   # commands with file names as arguments
   # Use @ character to avoid mistaken double word errors
   data_tmp = pattern['dir'].sub('@', data_tmp)
   data_tmp = pattern['literal'].sub('@', data_tmp)
   data_tmp = pattern['toc'].sub('@', data_tmp)
   data_tmp = pattern['http'].sub('@', data_tmp)
   data_tmp = pattern['directive'].sub('@', data_tmp)
   #
   # Must keep template file name error reporting
   # data_tmp = pattern['template'].sub('@', data_tmp)
   #
   # command with page names and headings as arguments
   data_tmp = pattern['ref_1'].sub('@', data_tmp)
   data_tmp = pattern['ref_2'].sub(r'\1', data_tmp)
   data_tmp = pattern['code'].sub('@', data_tmp)
   #
   # commands with external urls as arguments
   data_tmp = pattern['url_1'].sub('@', data_tmp)
   data_tmp = pattern['url_2'].sub(r'\1', data_tmp)
   #
   # latex \begin{command}
   data_tmp = pattern['tex_begin'].sub('@', data_tmp)
   #
   # any left over xrst commands
   data_tmp = re.sub( r'{xrst_comment_ch' , '@', data_tmp)
   #
   # previous_word
   previous_word = ''
   #
   # replace_word_list
   replace_word_list = list()
   #
   # m_obj
   for m_obj in pattern['word'].finditer( data_tmp ) :
      #
      # word, word_lower
      word       = m_obj.group(0)
      word_lower = word.lower()
      #
      if not word.startswith('@xrst_line') and word[0].isalpha()  :
         #
         # known
         # check if word is in dictionary or word_lower is special
         known =  spell_checker.known( word ) or word_lower in page_name_word
         if not known :
            #
            page_line, template_file, template_line = \
               xrst.file_line(m_obj, data_tmp)
            #
            # replace_word_list
            if not word_lower in replace_word_list :
               replace_word_list.append( word_lower )
            #
            # unknown_word_set
            if not word_lower in special_used :
               unknown_word_set.add( word_lower )
            #
            if not word_lower in special_used and print_warning :
               #
               # first_spell_warning
               if first_spell_warning :
                  msg  = '\nwarning: page_file = ' + page_file
                  msg += ', page_name = ' + page_name + '\n'
                  sys.stderr.write(msg)
                  first_spell_warning = False
               #
               # msg
               msg  = 'spelling = ' + word
               suggest = spell_checker.suggest(word)
               if suggest != None :
                  msg += f', suggest = {suggest}'
               msg += f', page_line = {page_line}'
               if template_file != None :
                  msg += f', template_file = {template_file}'
                  msg += f', template_line = {template_line}'
               msg += '\n'
               #
               sys.stderr.write(msg)
            #
            # special_used
            if word_lower in special_used :
               special_used[word_lower] = True
         #
         double_word = word_lower == previous_word.lower()
         if double_word :
            # This is the second use of word with only white space between
            #
            # replace_word_list
            if not word_lower in replace_word_list :
               replace_word_list.append( word_lower )
               replace_word_list.append( word_lower )
            else :
               index = replace_word_list.index( word_lower )
               assert 0 < index
               if index + 1 < len(replace_word_list) :
                  if replace_word_list[index + 1] != word_lower :
                     replace_word_list.insert(index, word_lower )
               else :
                  replace_word_list.append(word_lower)
            #
            if not word_lower in double_used and print_warning :
               # word is not in list of special double words
               #
               # first_spell_warning
               if first_spell_warning :
                  msg  = 'warning: file = ' + page_file
                  msg += ', page = ' + page_name + '\n'
                  sys.stderr.write(msg)
                  first_spell_warning = False
               #
               # line_number
               m_tmp = pattern['line'].search(data_tmp, m_obj.end() )
               assert m_tmp
               line_number = m_tmp.group(1)
               msg  = f'double word error: "{previous_word} {word}"'
               msg += ', line ' + line_number + '\n'
               sys.stderr.write(msg)
            #
            # double_used
            if word_lower in double_used :
               double_used[word_lower]  = True
      if not word.startswith('@xrst_line') :
         # previous_word
         # This captures when there are non space characters between words
         previous_word = word
   #
   # check for words that were not used
   for word_lower in special_used :
      ok = special_used[word_lower] or word_lower in double_used
      if print_warning and not ok :
         if first_spell_warning :
            msg  = '\nwarning: file = ' + page_file
            msg += ', page = ' + page_name + '\n'
            sys.stderr.write(msg)
            first_spell_warning = False
         msg = 'spelling word "' + word_lower + '" not needed\n'
         sys.stderr.write(msg)
   for word_lower in double_used :
      if not double_used[word_lower] and print_warning :
         if first_spell_warning :
            msg  = '\nwarning: file = ' + page_file
            msg += ', page = ' + page_name + '\n'
            sys.stderr.write(msg)
            first_spell_warning = False
         msg  = 'double word "' + word_lower + ' ' + word_lower
         msg += '" not needed\n'
         sys.stderr.write(msg)
   #
   # start_spell, end_spell
   if m_spell :
      m_line = pattern['line'].search(data_in, m_spell.start() )
      start_spell = int( m_line.group(1) )
      end_spell   = int( m_spell.group(3) )
   else :
      start_spell = 0
      end_spell   = 0
   #
   # begin_line
   # 2DO, remove this check (may not be valid in the future)
   m_line     = pattern['line'].search(data_in)
   check = int( m_line.group(1) )
   assert begin_line == check
   #
   # file_data
   file_data  = f'[ "{page_file}"."{page_name}" ]\n'
   file_data += f'begin_line = {begin_line}\n'
   file_data += f'start_spell = {start_spell}\n'
   file_data += f'end_spell = {end_spell}\n'
   if len(replace_word_list) == 0 :
      file_data += f'replace = []\n\n'
   else :
      file_data += f'replace = [\n'
      for word_lower in replace_word_list :
         file_data += f'   "{word_lower}",\n'
      file_data += ']\n\n'
   #
   # spell.toml
   file_obj   = open(f'{tmp_dir}/spell.toml', 'a')
   file_obj.write(file_data)
   file_obj.close()
   #
   # data_out
   data_out = pattern['spell_off'].sub( '', data_out)
   data_out = pattern['spell_on'].sub( '', data_out)
   #
   #
   spell_warning = not first_spell_warning
   # BEGIN_RETURN
   #
   assert type(data_out) == str
   assert type(spell_warning) == bool
   assert type(unknown_word_set) == set
   return data_out, spell_warning, unknown_word_set
   # END_RETURN
