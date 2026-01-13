#! /usr/bin/env python
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: Bradley M. Bell <bradbell@seanet.com>
# SPDX-FileContributor: 2020-25 Bradley M. Bell
# ----------------------------------------------------------------------------
import sys
import os
import re
import subprocess
# ----------------------------------------------------------------------------
pattern_return_newline    = re.compile( r'\r\n' )
pattern_include_backslash = re.compile( r'\.\. literalinclude:: .*\\' )
# ----------------------------------------------------------------------------
def get_index_page_name() :
   file_obj  = open('.readthedocs.yaml', 'r')
   file_data = file_obj.read()
   pattern   = r'\n *--index_page_name *([-._a-zA-Z0-9]*)'
   m_obj     = re.search(pattern, file_data)
   file_obj.close()
   return m_obj.group(1)
# ----------------------------------------------------------------------------
def get_rst_directory() :
   file_obj  = open('xrst.toml', 'r')
   file_data = file_obj.read()
   pattern   = r"\nrst_directory *= *'([^']*)'"
   m_obj     = re.search(pattern, file_data)
   file_obj.close()
   return m_obj.group(1)
# ----------------------------------------------------------------------------
def run_xrst(
   test_installed_version,
   test_external_links,
   suppress_spell_warnings,
) :
   index_page_name = get_index_page_name()
   #
   # python_executable
   python_executable = sys.executable
   #
   # command
   if test_installed_version :
      if not os.path.exists('build') :
         os.mkdir('build')
      os.chdir('build')
      command  = [ 'xrst', '--config_file', '../xrst.toml' ]
   else :
      command  = [ python_executable, '-m', 'xrst' ]
      command += [ '--config_file', 'xrst.toml' ]
      # sphinx_rtd_theme is in the tox.ini file as a dependency
      command += [ '--html_theme',      'sphinx_rtd_theme' ]
   if test_external_links :
      command += [ '--external_links' ]
   if suppress_spell_warnings :
      command += [ '--suppress_spell_warnings' ]
   #
   # command
   # This command should have the same group_list as the last group_list in
   # bin/check_xrst.sh which is used to keep the test_rst up to date.
   command += [
      '--local_toc',
      '--rst_only',
      '--index_page_name', index_page_name,
      '--group_list',      'default', 'user', 'dev',
   ]
   result = subprocess.run(command)
   assert result.returncode == 0
   #
   if test_installed_version :
      os.chdir('..')
# ----------------------------------------------------------------------------
def run_test(
   test_installed_version,
   test_external_links,
   suppress_spell_errors,
) :
   #
   # run_xrst
   run_xrst(
      test_installed_version,
      test_external_links,
      suppress_spell_errors
   )
   #
   # rst_list
   rst_directory = get_rst_directory()
   rst_list      = list()
   for entry in os.listdir(rst_directory) :
      if entry.endswith('.rst') :
         rst_list.append(entry)
   rst_list = sorted(rst_list)
   #
   # check_list
   check_list = sorted( os.listdir('test_rst') )
   #
   # rst_index, check_index
   rst_index   = 0
   check_index = 0
   while rst_index < len(rst_list) and check_index < len(check_list) :
      #
      # rst_name, check_name
      rst_name   = rst_list[rst_index]
      check_name = check_list[check_index]
      if rst_name < check_name :
         rst_index += 1
         assert False, f'{rst_name} is in {rst_directory} but not test_rst'
      elif check_name < rst_name :
         check_index += 1
         assert False, f'{check_name} is in test_rst but not {rst_directory}'
      else :
         #
         # rst_index, check_index
         rst_index     += 1
         check_index   += 1
         #
         # rst_file_data, check_file_data
         rst_file      = f'{rst_directory}/{rst_name}'
         check_file    = f'test_rst/{check_name}'
         #
         rst_file_obj   = open(rst_file, 'r')
         check_file_obj = open(check_file, 'r')
         #
         rst_data      = rst_file_obj.read()
         check_data    = check_file_obj.read()
         #
         rst_file_obj.close()
         check_file_obj.close()
         #
         # rst_data
         # dos2unix: relpace \r\n by \n
         replace  = r'\n'
         rst_data = pattern_return_newline.sub(replace, rst_data)
         #
         # rst_data
         # relpace \ in file names by /
         m_obj = pattern_include_backslash.search(rst_data)
         while m_obj != None :
            start      = m_obj.start()
            end        = m_obj.end()
            text       = m_obj.group(0)
            replace    = text.replace( '\\' , '/' )
            rst_data   = check_data[:start] + replace + rst_data[end:]
            m_obj      = pattern_include_backslash.search(rst_data)
         #
         if rst_data == check_data :
            print( f'{rst_name}: OK' )
         else :
            msg = f'{rst_file} is different from {check_file}'
            assert False, msg
# ----------------------------------------------------------------------------
def test_rst(
   test_installed_version  = False,
   test_external_links     = True,
   suppress_spell_warnings = False,
) :
   print( f'test_installed_version   = {test_installed_version}' )
   print( f'test_external_links      = {test_external_links}' )
   print( f'suppress_spell_warnings  = {suppress_spell_warnings}' )
   if not os.path.exists('xrst.toml') :
      assert False, 'test_rst.py: can not find xrst.toml in working directory'
   else :
      run_test(
         test_installed_version  ,
         test_external_links     ,
         suppress_spell_warnings ,
      )
# ----------------------------------------------------------------------------
if __name__ == '__main__' :
   #
   # usage
   usage   = 'usage: pytest/test_rst.py test_installed_version '
   usage  += 'test_external_links suppress_spell_warnings\n'
   usage  += 'where all the arguments are True or False'
   #
   # test_installed_version
   program = sys.argv[0]
   if program != 'pytest/test_rst.py' or len(sys.argv) != 4 :
      sys.exit(usage)
   for i in range(1, 4) :
      if sys.argv[i] not in [ 'True', 'False' ] :
         sys.exit(usage)
   test_installed_version  = sys.argv[1] == 'True'
   test_external_links     = sys.argv[2] == 'True'
   suppress_spell_warnings = sys.argv[3] == 'True'
   #
   test_rst(
         test_installed_version,
         test_external_links,
         suppress_spell_warnings
   )
