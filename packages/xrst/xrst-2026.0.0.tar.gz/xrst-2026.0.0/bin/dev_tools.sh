#! /usr/bin/env bash
set -e -u
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: Bradley M. Bell <bradbell@seanet.com>
# SPDX-FileContributor: 2020-25 Bradley M. Bell
# -----------------------------------------------------------------------------
if [ $# != 1 ] && [ $# != 2 ]
then
cat << EOF
usage: bin/devel_tools.sh dest_repo [spdx_license_id]

Copies the current development tools from xrst.git to dest_repo

If spdx_license_id is not present, dest_repo/bin/dev_settings.sh must already
exist and contain value of spdx_license_id for the packare in dest_repo.
EOF
   exit 1
fi
#
# dest_repo
dest_repo="$1"
if [ ! -d "$dest_repo/.git" ]
then
   echo "dev_tools.sh: $dest_repo is not a git repository"
   exit 1
fi
if [ ! -d "$dest_repo/bin" ]
then
   echo "dev_tools.sh: $dest_repo/bin is not a directory"
   exit 1
fi
#
# spdx_license_id
if [ $# == 1 ]
then
   file="$dest_repo/bin/dev_settings.sh"
   if [ ! -e $file ]
   then
      echo 'dev_tools.sh: spdx_license not specified and can not find'
      echo $file
      exit 1
   fi
   #
   # spdx_license_id
   source $dest_repo/bin/dev_settings.sh
   if [ -z ${spdx_license_id+word} ]
   then
      echo "dev_tools.sh: spd_license_id is not set in $file"
      exit 1
   fi
else
   spdx_license_id="$2"
fi
#
# sed
source bin/grep_and_sed.sh
# -----------------------------------------------------------------------------
# dev_tools
# BEGIN_SORT_THIS_LINE_PLUS_2
dev_tools='
   bin/check_copy.sh
   bin/check_invisible.sh
   bin/check_sort.sh
   bin/check_tab.sh
   bin/check_version.sh
   bin/dev_settings.sh
   bin/git_commit.sh
   bin/grep_and_sed.sh
   bin/new_release.sh
   bin/sort.sh
'
# END_SORT_THIS_LINE_MINUS_2
if [ -e "$dest_repo/xrst.toml" ]
then
   dev_tools+='
      .readthedocs.yaml
      bin/group_list.sh
      bin/run_xrst.sh
   '
fi
if [ -e "$dest_repo/pyproject.toml" ]
then
   dev_tools+='
      bin/twine.sh
   '
fi
for file in $dev_tools
do
   if [ $file == bin/dev_settings.sh ] \
   || [ $file == bin/grep_and_sed.sh ] \
   || [ $file == .readthedocs.yaml ]
   then
      if [ -x $file ]
      then
         echo "$file is executable"
         exit 1
      fi
   else
      if [ ! -x $file ]
      then
         echo "$file is not executable"
         exit 1
      fi
      line_two=$($sed -n -e '2,2p' $file)
      if [ "$line_two" != 'set -e -u' ]
      then
         echo "Line 2 of $file is not equal to:"
         echo 'set -e -u'
         exit 1
      fi
   fi
done
#
# xrst_repo
xrst_repo=$(pwd)
#
# dest_repo
cd $dest_repo
dest_repo=$(pwd)
#
# sed.$$
cat << EOF > sed.$$
s|\\(SPDX-License-Identifier:\\) GPL-3.0-or-later|\\1 $spdx_license_id|
s|^spdx_license_id=.*|spdx_license_id='$spdx_license_id'|
EOF
#
# check for overwriting changes
for file in $dev_tools
do
   dest_path="$dest_repo/$file"
   xrst_path="$xrst_repo/$file"
   $sed -f sed.$$ $xrst_path > temp.$$
   if [ -e $dest_path ]
   then
      if ! diff $dest_path temp.$$ > /dev/null
      then
         temp=$(git ls-files $file)
         if [ "$temp" == '' ]
         then
            echo "$dest_path"
            echo 'not in repository and would be overwritten by dev_tools.sh'
            rm temp.$$
            rm sed.$$
            exit 1
         else
            if ! git diff --exit-code $file > /dev/null
            then
               echo "$dest_path"
               echo 'is in repository and has changes that are not checked in'
               rm temp.$$
               rm sed.$$
               exit 1
            fi
         fi
      fi
   fi
done
rm temp.$$
#
# package_name, ... , invisible_and_tab_ok
package_name=''
index_page_name=''
version_file_list=''
no_copyright_list=''
invisible_and_tab_ok=''
check_git_commit=''
contributor_list=''
if [ -e $dest_repo/bin/dev_settings.sh ]
then
   source $dest_repo/bin/dev_settings.sh
fi
#
# year, release
if [ -e $dest_repo/bin/new_release.sh ]
then
   cmd=$( $sed -n -e '/^year=.*/p' $dest_repo/bin/new_release.sh )
   eval $cmd
   cmd=$( $sed -n -e '/^release=.*/p' $dest_repo/bin/new_release.sh )
   eval $cmd
else
   year=''
   release=''
fi
#
# $des_repo/bin/*.sh
echo "Copying the following tools to $dest_repo"
echo "while setting SPDX-License-Identifier to $spdx_license_id"
echo 'see the comments at the top of each file for its usage:'
line='# !! EDITS TO THIS FILE ARE LOST DURING UPDATES BY'
line+=' xrst.git/bin/dev_tools.sh !!'
for file in $dev_tools
do
   echo "  $file"
   dest_path="$dest_repo/$file"
   xrst_path="$xrst_repo/$file"
   $sed -f sed.$$ $xrst_path > $dest_path
   if [ -x "$xrst_path" ]
   then
      chmod +x $dest_path
   fi
   if [ "$file" == '.readthedocs.yaml' ]
   then
      $sed -i $file -e "1,1s|^|$line\n|"
   elif [ "$file" != 'bin/dev_settings.sh' ]
   then
      $sed -i $file -e "s|^set -e -u|&\\n$line|"
   fi
done
#
# $dest_repo/bin/new_release.sh
$sed -i $dest_repo/bin/new_release.sh \
   -e "s|^year=[^#]*#|year='$year' #|" \
   -e "s|^release=[^#]*#|release='$release' #|"
#
# $dest_repo/.readthedocs.yaml
if [ -e "$dest_repo/xrst.toml" ]
then
   group_list=$( bin/group_list.sh | \
      $sed -e 's|^| |' -e 's|$| |' -e 's| dev ||' -e 's|^ *||' -e 's| *$||' )
   $sed -r -i $dest_repo/.readthedocs.yaml \
      -e "s|^( *--index_page_name).*|\\1 $index_page_name|" \
      -e "s|^( *--group_list).*|\\1 $group_list|" \
      -e '/\{xrst_begin /d' \
      -e '/\{xrst_end /d'
fi
#
# $dest_repo/bin/dev_settings.sh
cat << EOF > sed.$$
/^version_file_list=' *$/! b one
: loop_1
N
/\\n' *$/! b loop_1
s|.*|@version_file_list@|
#
: one
/^no_copyright_list=' *$/! b two
: loop_2
N
/\\n' *$/! b loop_2
s|.*|@no_copyright_list@|
#
: two
/^invisible_and_tab_ok=' *$/! b three
: loop_3
N
/\\n' *$/! b loop_3
s|.*|@invisible_and_tab_ok@|
#
: three
/^check_git_commit=' *$/! b four
: loop_4
N
/\\n' *$/! b loop_4
s|.*|@check_git_commit@|
#
: four
/^contributor_list=' *$/! b five
: loop_5
N
/\\n' *$/! b loop_5
s|.*|@contributor_list@|
#
: five
EOF
$sed -i $dest_repo/bin/dev_settings.sh -f sed.$$
rm sed.$$
#
# $dest_repo/bin/dev_settings.sh
$sed -i $dest_repo/bin/dev_settings.sh \
   -e "s|^package_name=.*|package_name='$package_name'|" \
   -e "s|^index_page_name=.*|index_page_name='$index_page_name'|"
for variable in \
   version_file_list \
   no_copyright_list \
   contributor_list \
   invisible_and_tab_ok \
   check_git_commit
do
   replace=$(echo ${!variable} | $sed -e 's|[ \n]|\\n   |g' -e 's|^|   |')
   if [[ "$replace" =~ ^( *)$ ]]
   then
      $sed -i $dest_repo/bin/dev_settings.sh \
         -e "s|@$variable@|$variable='\n'|"
   else
      $sed -i $dest_repo/bin/dev_settings.sh \
         -e "s|@$variable@|$variable='\n$replace\n'|"
   fi
done
# -----------------------------------------------------------------------------
echo 'The following variables are empty and may need to be corrected ?'
echo 'The variable check_git_commit is usually empty. The settings are in'
echo "$dest_repo/bin/dev_settings.sh"
for variable in  \
   package_name \
   index_page_name \
   version_file_list \
   contributor_list \
   no_copyright_list \
   invisible_and_tab_ok \
   check_git_commit
do
   non_space=$(echo ${!variable} | sed -e 's| ||g')
   if [ "$non_space" == '' ]
   then
      echo "  $variable"
   fi
done
echo 'If a setting is incorrect, abort the changes except for dev_setting.sh,'
echo 'fix the settings in dev_setting.sh, commit fix, and re-run dev_tools.sh.'
echo
echo 'dev_tools.sh: OK'
exit 0
