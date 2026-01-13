#! /usr/bin/env bash
set -e -u
#
# git ls-files: list files in the git repository
# sed:          remove files in the test_rst directory
git ls-files | sed -e '/^test_rst[/]/d'
