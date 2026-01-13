.. _temporary_file-name:

!!!!!!!!!!!!!!
temporary_file
!!!!!!!!!!!!!!

.. meta::
   :keywords: temporary_file,write,the,temporary,rst,file,for,a,page,prototype,page_source,target,pseudo_heading,file_in,tmp_dir,page_name,file_out,data_in,rst2xrst_list

.. index:: temporary_file, write, temporary, rst, page

.. _temporary_file-title:

Write the temporary RST file for a page
#######################################

.. contents::
   :local:

.. index:: prototype

.. _temporary_file@Prototype:

Prototype
*********

.. literalinclude:: ../../xrst/temporary_file.py
   :lines: 105-120,231-237
   :language: py

.. index:: page_source

.. _temporary_file@page_source:

page_source
***********
If *page_source* is true and *target* is html,
a link to the xrst source code is included at the
top of each page.
If *page_source* is true and *target* is tex,
the location of the xrst source code is reported at the
top of each page.

.. index:: target

.. _temporary_file@target:

target
******
If the :ref:`run_xrst@target` command line argument.

.. index:: pseudo_heading

.. _temporary_file@pseudo_heading:

pseudo_heading
**************
is the :ref:`process_headings@pseudo_heading` for this page.

.. index:: file_in

.. _temporary_file@file_in:

file_in
*******
is the name of the xrst input file for this page.

.. index:: tmp_dir

.. _temporary_file@tmp_dir:

tmp_dir
*******
is the directory where the output file will be saved.

.. index:: page_name

.. _temporary_file@page_name:

page_name
*********
is the name of this page.

.. index:: file_out

.. _temporary_file@file_out:

file_out
********
The temporary file written by the routine, *file_out* , is
tmp_dir/page_name.rst.

.. index:: data_in

.. _temporary_file@data_in:

data_in
*******
is the data for this page with all the xrst commands converted to
their sphinx RST values, except the \\n\{xrst\@before_title} command.
The following is added to this data before writing it to the output file:

 #. The preamble is included at the beginning.
 #. If *target* is ``html`` :

    #. The *page_name* ``-name`` label is added next.
    #. The pseudo heading is added next.
    #. The name of the input file *file_in* is added next.

 #. If *target* is ``tex`` :
    All cross references of the form :ref:\` *page_name* -name \` ,
    are changed to :ref:\` *page_name* < *page_name* -title >\` .
    Note that the page name will be added to the title when
    :ref:`add_before_title-name` is called during
    :ref:`table_of_contents-name` .

 #. Check for an xrst command that was not recognized.
 #. Any sequence of more than 2 lines
    with only tabs or space are converted to 2 empty lines.
 #. Empty lines at the end are removed
 #. The xrst_line_number entries are removed.
 #. The xrst_template_begin and xrst_template_end markers are removed.
 #. The text ``\{xrst_`` is replaced by ``{xrst_`` .

.. index:: rst2xrst_list

.. _temporary_file@rst2xrst_list:

rst2xrst_list
*************
This is the value returned by ``temporary_file`` .
For each *index*, *rst2xrst_list* [ *index* ] is the a tuple; see
:ref:`remove_line_numbers@rst2xrst_list` .
