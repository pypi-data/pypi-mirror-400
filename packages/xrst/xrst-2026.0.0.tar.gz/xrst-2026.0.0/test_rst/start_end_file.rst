.. _start_end_file-name:

!!!!!!!!!!!!!!
start_end_file
!!!!!!!!!!!!!!

.. meta::
   :keywords: start_end_file,convert,literal,command,start,,end,from,text,to,line,numbers,prototype,page_file,page_name,input_file,display_file,cmd_line,start_after,end_before,start_line,end_line,m_start,m_end,m_data

.. index:: start_end_file, convert, literal, start,, end, from, text, line, numbers

.. _start_end_file-title:

Convert literal command start, end from text to line numbers
############################################################

.. contents::
   :local:

.. index:: prototype

.. _start_end_file@Prototype:

Prototype
*********

.. literalinclude:: ../../xrst/start_end_file.py
   :lines: 89-112,189-192
   :language: py

.. index:: page_file

.. _start_end_file@page_file:

page_file
*********
is the name of the file that contains the begin command for this page.
This is different from the current input file if we are processing
a template expansion.

.. index:: page_name

.. _start_end_file@page_name:

page_name
*********
is the name of the page where the xrst_literal command appears.

.. index:: input_file

.. _start_end_file@input_file:

input_file
**********
is the name of the file where the xrst_literal command appears.
This is different for *page_file* when the command appears in a
template expansion.

.. index:: display_file

.. _start_end_file@display_file:

display_file
************
is the name of the file that we are displaying. If it is not the same as
input_file, then it must have appeared in the xrst_literal command.

.. index:: cmd_line

.. _start_end_file@cmd_line:

cmd_line
********
If input_file is equal to display_file, the lines of the file
between line numbers cmd_line[0] and cmd_line[1] inclusive
are in the xrst_literal command and are excluded from the search.

.. index:: start_after

.. _start_end_file@start_after:

start_after
***********
is the starting text. There must be one and only one copy of this text in the
file (not counting the excluded text). This text has no newlines and cannot
be empty.  If not, an the error is reported and the program stops.

.. index:: end_before

.. _start_end_file@end_before:

end_before
**********
is the stopping text. There must be one and only one copy of this text in the
file (not counting the excluded text). This text has no newlines and cannot
be empty.  Furthermore, the stopping text must come after the end of the
starting text. If not, an the error is reported and the program stops.

.. index:: start_line

.. _start_end_file@start_line:

start_line
**********
is the line number where start_after appears.

.. index:: end_line

.. _start_end_file@end_line:

end_line
********
is the line number where end_before appears.

.. index:: m_start

.. _start_end_file@m_start:

m_start
*******
is a match object corresponding to the location of start_after.
It is only used for reporting errors.

.. index:: m_end

.. _start_end_file@m_end:

m_end
*****
is a match object corresponding to the location of end_before.
It is only used for reporting errors.

.. index:: m_data

.. _start_end_file@m_data:

m_data
******
is the data for the entire page, including template expansion.
It corresponds to *m_start* , *m_end* and is only used for reporting errors.
