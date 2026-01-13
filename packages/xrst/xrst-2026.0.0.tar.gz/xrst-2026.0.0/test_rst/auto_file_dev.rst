.. _auto_file_dev-name:

!!!!!!!!!!!!!
auto_file_dev
!!!!!!!!!!!!!

.. meta::
   :keywords: auto_file_dev,create,the,automatically,generated,files,conf_dict,rst_dir,tmp_dir,link_timeout,html_theme,target,all_page_info,root_page_list,tmp_dir/xrst_contents.rst,tmp_dir/xrst_index.rst,tmp_dir/xrst_search.rst,tmp_dir/xrst_search.js,tmp_dir/xrst_root_doc.rst,rst_dir/_sources,rst_dir/conf.py,prototype

.. index:: auto_file_dev, create, automatically, generated, files

.. _auto_file_dev-title:

Create the automatically generated files
########################################

.. contents::
   :local:

.. index:: conf_dict

.. _auto_file_dev@conf_dict:

conf_dict
*********
is a python dictionary representation of the configuration file.

.. index:: rst_dir

.. _auto_file_dev@conf_dict@rst_dir:

rst_dir
=======
we use *rst_dir* to denote *conf_dict* ['directory']['rst_directory'] .

.. index:: tmp_dir

.. _auto_file_dev@conf_dict@tmp_dir:

tmp_dir
=======
we use *tmp_dir* to denote *rst_dir*\ /tmp .
This is the directory where xrst creates a temporary copy of *rst_dir* .
These files are also automatically generated.

.. index:: link_timeout

.. _auto_file_dev@link_timeout:

link_timeout
************
The link_timeout determine by the xrst command line.

.. index:: html_theme

.. _auto_file_dev@html_theme:

html_theme
**********
The html_theme determined by the xrst command line.

.. index:: target

.. _auto_file_dev@target:

target
******
is html or tex

.. index:: all_page_info

.. _auto_file_dev@all_page_info:

all_page_info
*************
is a list with length equal to the number of pages.
with the following key, value pairs (all the keys are strings):

.. csv-table::
    :header: key, value

    page_name, (str) containing the name of this page.
    page_title,  (str) containing the title for this page.
    parent_page, (int) index in all_page_info for the parent of this page.
    in_parent_file, (bool) is this page in same input file as its parent.
    keywords, (str) space separated list of index entries for this page.
    file_in, (str) name of the input file for this page
    begin_line, (int) line number where begin command is for this page
    end_line, (int) line number where end command is for this page
    template_list, (list of str) name of template files used by this page

.. index:: root_page_list

.. _auto_file_dev@root_page_list:

root_page_list
**************
is a list of the root page names (one for each group) in the order
they will appear in the table of contents.

.. index:: tmp_dir/xrst_contents.rst

.. _auto_file_dev@tmp_dir/xrst_contents.rst:

tmp_dir/xrst_contents.rst
*************************
This file creates is the table of contents for the documentation.
It has the label xrst_contents which can be used to link
to this page.

.. index:: tmp_dir/xrst_index.rst

.. _auto_file_dev@tmp_dir/xrst_index.rst:

tmp_dir/xrst_index.rst
**********************
This file just contains a link to the genindex.rst file.
It is (is not) included if target is html (tex).

.. index:: tmp_dir/xrst_search.rst

.. _auto_file_dev@tmp_dir/xrst_search.rst:

tmp_dir/xrst_search.rst
***********************
This file contains the xrst search utility.
It is (is not) included if target is html (tex).

.. index:: tmp_dir/xrst_search.js

.. _auto_file_dev@tmp_dir/xrst_search.js:

tmp_dir/xrst_search.js
**********************
This file contains the java script used by xrst_search.rst.
It is (is not) included if target is html (tex).

.. index:: tmp_dir/xrst_root_doc.rst

.. _auto_file_dev@tmp_dir/xrst_root_doc.rst:

tmp_dir/xrst_root_doc.rst
*************************
This is the root level in the sphinx documentation tree.

.. index:: rst_dir/_sources

.. _auto_file_dev@rst_dir/_sources:

rst_dir/_sources
****************
The sub-directory is used to store the replacement
for the _sources directory. This contains the xrst sources that were used
to create the rst files that sphinx used as sources.
This is (is not) included if target is html (tex).
If target is html, this sub-directory must exist and should be empty,
before calling auto_file.

.. index:: rst_dir/conf.py

.. _auto_file_dev@rst_dir/conf.py:

rst_dir/conf.py
***************
This is the configuration file used by sphinx to build the documentation.

.. index:: prototype

.. _auto_file_dev@Prototype:

Prototype
*********

.. literalinclude:: ../../xrst/auto_file.py
   :lines: 406-413
   :language: py
