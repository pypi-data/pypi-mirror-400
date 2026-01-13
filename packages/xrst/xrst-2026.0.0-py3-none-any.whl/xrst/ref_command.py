# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: Bradley M. Bell <bradbell@seanet.com>
# SPDX-FileContributor: 2020-23 Bradley M. Bell
# ----------------------------------------------------------------------------
r"""
{xrst_begin ref_cmd user}

Allow Multiple Lines in Sphinx ref Role
#######################################

Syntax
******

| ``:ref:`` ` *target* `
| ``:ref:`` ` *linking_text* ``<``  *target* ``>`` `

Purpose
*******
The xrst program allows one to place a sphinx ``ref`` role target
on multiple lines.
This makes the xrst input more readable
when the headings corresponding to the target are long; see
:ref:`heading_links-name` .

New Lines
*********
Newlines and spaces surrounding newlines are removed  from *target* .

Example
*******
:ref:`ref_example-name`

{xrst_end ref_cmd}
"""
# ----------------------------------------------------------------------------
import re
import os
import xrst
#
# ref_pattern
ref_pattern_one = re.compile( r':ref:`([^<`]+)`' )
ref_pattern_two = re.compile( r':ref:`([^<`]*)<([^>]*)> *`' )
line_pattern    = re.compile(  r'@xrst_line ([0-9]+)@\n *' )
#
#
# {xrst_begin ref_cmd_dev dev}
# {xrst_comment_ch #}
#
# Remove Leading and Trailing White Space From ref Role Targets
# #############################################################
#
# Prototype
# *********
# {xrst_literal ,
#    # BEGIN_DEF, # END_DEF
#    # BEGIN_RETURN, # END_RETURN
# }
#
# data_in
# *******
# is the data for this page.
#
# data_out
# ********
# The return data_out is a copy of data_in except that white space
# surrounding the target components has been removed .
#
# {xrst_end ref_cmd_dev}
# BEGIN_DEF
def ref_command(data_in) :
   assert type(data_in) == str
   # END_DEF
   #
   # data_out
   data_out = data_in
   #
   # offset
   offset = 0
   #
   # m_ref
   m_ref  = ref_pattern_one.search(data_out, offset)
   while m_ref != None :
      #
      # data_before, data_after
      data_before  = data_out[: m_ref.start()]
      data_after   = data_out[m_ref.end() :]
      #
      # target
      target = m_ref.group(1)
      #
      # target
      target = line_pattern.sub('', target)
      #
      # data_middle
      data_middle = f':ref:`{target}`'
      #
      # data_out
      data_out = data_before + data_middle + data_after
      #
      # offset
      offset = len( data_before + data_middle )
      #
      # m_ref
      m_ref = ref_pattern_one.search(data_out, offset)
   #
   # offset
   offset = 0
   #
   # m_ref
   m_ref  = ref_pattern_two.search(data_out, offset)
   while m_ref != None :
      #
      # data_before, data_after
      data_before  = data_out[: m_ref.start()]
      data_after   = data_out[m_ref.end() :]
      #
      # linking_text, target
      linking_text = m_ref.group(1)
      target       = m_ref.group(2)
      #
      # target
      target = line_pattern.sub('', target)
      #
      # data_middle
      data_middle = f':ref:`{linking_text}<{target}>`'
      #
      # data_out
      data_out = data_before + data_middle + data_after
      #
      # offset
      offset = len( data_before + data_middle )
      #
      # m_ref
      m_ref = ref_pattern_two.search(data_out, offset)
   #
   # BEGIN_RETURN
   #
   assert type(data_out) == str
   return data_out
   # END_RETURN
