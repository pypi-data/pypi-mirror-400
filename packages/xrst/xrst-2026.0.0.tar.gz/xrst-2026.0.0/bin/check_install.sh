#! /usr/bin/env bash
set -e -u
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: Bradley M. Bell <bradbell@seanet.com>
# SPDX-FileContributor: 2020-25 Bradley M. Bell
# -----------------------------------------------------------------------------
if [ "$0" != "bin/check_install.sh" ]
then
   echo "bin/check_install.sh: must be executed from its parent directory"
   exit 1
fi
# -----------------------------------------------------------------------------
#
# prefix
prefix="$(pwd)/build/prefix"
#
# test_driver
test_driver='pytest/test_rst.py'
#
# install
# this installs below the build directory
pip install --prefix=$prefix .
#
# site_packages
site_packages="$(find $prefix -name 'site-packages')"
if [ "$site_packages" == '' ]
then
   echo "bin/check_install.sh: cannot find site-packages below $prefix"
   exit 1
fi
#
# PYTHONPATH
for dir in $site_packages
do
   #
   # PYTHONPATH
   if [ -z "${PYTHONPATH+x}" ]
   then
      PYTHONPATH="$dir"
   elif [ "$PYTHONPATH" == '' ]
   then
      PYTHONPATH="$dir"
   else
      PYTHONPATH="$dir:$PYTHONPATH"
   fi
done
export PYTHONPATH
#
# PATH
PATH="$prefix/bin:$PATH"
if ! which xrst | grep "$prefix/bin/xrst\$" > /dev/null
then
   echo "bin/check_install.sh: which_xrst = $(which_xrst)"
   exit
fi
#
# pytest/test_rst.py
test_installed_version='True'
skip_external_links='True'
suppress_spell_warnings='True'
pytest/test_rst.py \
   $test_installed_version \
   $skip_external_links \
   $suppress_spell_warnings
#
# install
# this restores a normal install of xrst
pip install .
#
# -----------------------------------------------------------------------------
echo 'check_install.sh: OK'
exit 0
