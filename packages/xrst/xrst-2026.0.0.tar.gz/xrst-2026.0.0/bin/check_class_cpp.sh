#! /usr/bin/env bash
set -e -u
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: Bradley M. Bell <bradbell@seanet.com>
# SPDX-FileContributor: 2020-22 Bradley M. Bell
# -----------------------------------------------------------------------------
# bash function that echos and executes a command
echo_eval() {
   echo $*
   eval $*
}
# -----------------------------------------------------------------------------
if [ "$0" != "bin/check_class_cpp.sh" ]
then
   echo "bin/check_class_cpp.sh: must be executed from its parent directory"
   exit 1
fi
if [ ! -e build ]
then
   mkdir build
fi
echo_eval g++ example/class.cpp -o build/class
if ! build/class
then
   echo 'check_cpass_cpp.sh: Error'
   exit 1
fi
echo 'check_class_cpp.sh: OK'
exit 0
