.. _table_of_contents-name:

!!!!!!!!!!!!!!!!!
table_of_contents
!!!!!!!!!!!!!!!!!

.. meta::
   :keywords: table_of_contents,create,the,table,of,contents,and,modify,titles,prototype,tmp_dir,target,tex,html,all_page_info,root_page_list,content

.. index:: table_of_contents, create, table, contents, modify, titles

.. _table_of_contents-title:

Create the table of contents and Modify Titles
##############################################

.. contents::
   :local:

.. index:: prototype

.. _table_of_contents@Prototype:

Prototype
*********

.. literalinclude:: ../../xrst/table_of_contents.py
   :lines: 213-222,253-255
   :language: py

.. index:: tmp_dir

.. _table_of_contents@tmp_dir:

tmp_dir
*******
is the temporary directory where the temporary rst files are written.

.. index:: target

.. _table_of_contents@target:

target
******
is either 'html' or 'tex'.

.. index:: tex

.. _table_of_contents@target@tex:

tex
===
If target is 'tex',  for each temporary file
tmp_dir/page_name.rst the text \\n\{xrst\@before_title}
is removed and the page number followed by the page name is added
at the front of the title for the page.
The page number includes the counter for each level.

.. index:: html

.. _table_of_contents@target@html:

html
====
If target is 'html',
\\n\{xrst\@before_title} is removed without other changes.

.. index:: all_page_info

.. _table_of_contents@all_page_info:

all_page_info
*************
is a list with length equal to the number of pages.
The value all_page_info[page_index] is a dictionary for this page
with the following key, value pairs (all the keys are strings):

..  csv-table::
    :header: key, value, type

    page_name, contains the name of this page, str
    page_title,  contains the title for this page, str
    parent_page, index in all_page_info for the parent of this page, int
    in_parent_file, is this page in same input file as its parent, bool

.. index:: root_page_list

.. _table_of_contents@root_page_list:

root_page_list
**************
is a list of strings containing the root page name for each group.
The order of the root page names determine the order of the groups
int the table of contents.

.. index:: content

.. _table_of_contents@content:

content
*******
The return content is the table of contents entries for all the pages.
The following are placed at the beginning of the of content.

1.  The page name xrst_contents and corresponding label xrst_contents-name
2.  The page title Table of Contents and corresponding label
    xrst_contents-title
