#! /usr/bin/env bash
set -e -u
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: Bradley M. Bell <bradbell@seanet.com>
# SPDX-FileContributor: 2020-25 Bradley M. Bell
# ----------------------------------------------------------------------------
# bash function that echos and executes a command
function echo_eval {
   echo $*
   eval $*
}
# -----------------------------------------------------------------------------
# bash function that prompts [yes/no] and returns (exits 1) on yes (no)
function continue_yes_no {
   read -p '[yes/no] ? ' response
   while [ "$response" != 'yes' ] && [ "$response" != 'no' ]
   do
      echo "response = '$response' is not yes or no"
      read -p '[yes/no] ? ' response
   done
   if [ "$response" == 'no' ]
      then exit 1
   fi
}
# -----------------------------------------------------------------------------
if [ "$0" != "bin/check_xrst.sh" ]
then
   echo "bin/check_xrst.sh: must be executed from its parent directory"
   exit 1
fi
#
# external_links, suppress_spell_warnings
external_links='yes'
suppress_spell_warnings='no'
while [ "$#" != 0 ]
do
   case "$1" in

      --skip_external_links)
      external_links='no'
      ;;

      --suppress_spell_warnings)
      suppress_spell_warnings='yes'
      ;;

      *)
      echo "bin/check_xrst.sh: command line argument "$1" is not"
      echo '--skip_external_links or --suppress_spell_warnings'
      exit 1
      ;;
   esac
   #
   shift
done
# -----------------------------------------------------------------------------
#
# PYTHON_PATH
if [ -z ${PYTHONPATH+x} ]
then
   export PYTHONPATH="$(pwd)"
else
   export PYTHONPATH="$(pwd):$PYTHONPATH"
fi
echo "PYTHONPATH=$PYTHONPATH"
#
# number_jobs
if which nproc >& /dev/null
then
   n_proc=$(nproc)
else
   n_proc=$(sysctl -n hw.ncpu)
fi
if [ $n_proc == '1' ] || [ n_proc == '2' ]
then
   number_jobs='1'
else
   let number_jobs="$n_proc - 1"
fi
#
# index_page_name
index_page_name=$(\
   sed -n -e '/^ *--index_page_name*/p' .readthedocs.yaml | \
   sed -e 's|^ *--index_page_name *||' \
)
# -------------------------------------------------------------------------
# build directory
# -------------------------------------------------------------------------
# run from build directory to test when project_directory not working directory
if [ ! -e build ]
then
   mkdir build
fi
cd    build
#
# build/xrst.toml
sed -e "s|^project_directory *=.*|project_directory = '..'|"  \
   ../xrst.toml > xrst.toml
#
# group_list
for group_list in 'default' 'default user dev'
do
   # build/html, build/rst
   for subdir in html rst
   do
      if [ -e $subdir ]
      then
         echo_eval rm -r $subdir
      fi
   done
   #
   # args
   args='--local_toc'
   if [ "$group_list" == 'default' ]
   then
      args+=" --config_file ../xrst.toml"
   else
      args+=" --index_page_name $index_page_name"
      args+=" --config_file xrst.toml"
   fi
   args+=" --group_list $group_list"
   args+=" --html_theme sphinx_rtd_theme"
   args+=" --number_jobs $number_jobs"
   if [ "$suppress_spell_warnings" == 'yes' ]
   then
      args+=' --suppress_spell_warnings'
   fi
   #
   # build/html, build/rst
   # last group_list should have same arguments as in pytest/test_rst.py
   echo "python -m xrst $args"
   if ! python -m xrst $args 2> check_xrst.$$
   then
      type_error='error'
   else
      type_error='warning'
   fi
   if [ -s check_xrst.$$ ]
   then
      cat check_xrst.$$
      rm check_xrst.$$
      echo "$0: exiting due to $type_error above"
      exit 1
   fi
   rm check_xrst.$$
done
# -----------------------------------------------------------------------------
# project directory
cd ..
# -----------------------------------------------------------------------------
#
# rst_dir, file
rst_dir='build/rst'
file_list=$(ls -a $rst_dir/*.rst | sed -e "s|^$rst_dir/||" )
for file in .readthedocs.yaml.rst $file_list
do
   if [ ! -e test_rst/$file ]
   then
      echo "The output file test_rst/$file does not exist."
      echo 'Should we use the following command to fix this'
      echo "    cp $rst_dir/$file test_rst/$file"
      continue_yes_no
      cp $rst_dir/$file test_rst/$file
   elif ! diff test_rst/$file $rst_dir/$file
   then
      echo "$rst_dir/$file changed; above is output of"
      echo "    diff test_rst/$file $rst_dir/$file"
      echo 'Should we use the following command to fix this'
      echo "    cp $rst_dir/$file test_rst/$file"
      continue_yes_no
      cp $rst_dir/$file test_rst/$file
   else
      echo "$file: OK"
   fi
done
#
# file
file_list=$(ls -a test_rst/*.rst | sed -e "s|^test_rst/||" )
for file in $file_list
do
   if [ ! -e build/rst/$file ]
   then
      echo "The output file build/rst/$file does not exist."
      echo 'Should we use the following command to remove it form test_rst'
      echo "    git rm -f test_rst/$file"
      continue_yes_no
      git rm -f test_rst/$file
   fi
done
#
# external_links
if [ "$external_links" == 'yes' ]
then
   cd build
   echo "python -m xrst $args --external_links --continue_with_warnings"
   python -m xrst $args --external_links --continue_with_warnings
fi
# -----------------------------------------------------------------------------
echo
echo "$0: OK"
exit 0
