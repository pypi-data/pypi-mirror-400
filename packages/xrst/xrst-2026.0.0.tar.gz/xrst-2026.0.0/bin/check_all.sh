#! /usr/bin/env bash
set -e -u
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: Bradley M. Bell <bradbell@seanet.com>
# SPDX-FileContributor: 2020-25 Bradley M. Bell
# -----------------------------------------------------------------------------
# echo_eval
echo_eval() {
   echo $*
   eval $*
}
# -----------------------------------------------------------------------------
if [ "$0" != "bin/check_all.sh" ]
then
   echo "bin/check_all.sh: must be executed from its parent directory"
   exit 1
fi
#
# external_links, suppress_spell_warnings
flags=''
while [ "$#" != 0 ]
do
   case "$1" in

      --skip_external_links)
      flags+=" $1"
      ;;

      --suppress_spell_warnings)
      flags+=" $1"
      ;;

      *)
      echo "bin/check_all.sh: command line argument "$1" is not"
      echo '--skip_external_links or --suppress_spell_warnings'
      exit 1
      ;;
   esac
   #
   shift
done
#
# sed
source bin/grep_and_sed.sh
#
# check_list
check_list=$(ls bin/check_* | $sed \
   -e '/^bin[/]check_xrst.sh/d' \
   -e '/^bin[/]check_all.sh/d' \
)
for check in $check_list
do
   echo_eval $check
done
#
# bin/check_xrst.sh
echo_eval bin/check_xrst.sh $flags
#
# tox
if [ "$flags" == '' ]
then
   tox
fi
#
echo "check_all.sh $flags: OK"
exit 0
