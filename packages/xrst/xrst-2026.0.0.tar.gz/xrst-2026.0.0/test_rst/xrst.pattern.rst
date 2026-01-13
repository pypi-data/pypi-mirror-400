.. _xrst.pattern-name:

!!!!!!!!!!!!
xrst.pattern
!!!!!!!!!!!!

.. meta::
   :keywords: xrst.pattern,the,dictionary,pattern,begin,code,comment_ch,dir,end,line,literal,template_begin,template_end,toc

.. index:: xrst.pattern, xrst.pattern, dictionary

.. _xrst.pattern-title:

The xrst.pattern Dictionary
###########################

.. contents::
   :local:

.. index:: pattern

.. _xrst.pattern@pattern:

pattern
*******
This dictionary contains compiled regular expressions.
It does not change after its initial setting when this file is imported.

.. literalinclude:: ../../xrst/pattern.py
   :lines: 19-19
   :language: py

.. index:: begin

.. _xrst.pattern@begin:

begin
*****
Pattern for the begin command.

0. preceding character or empty + the command.
1. preceding character or empty
2. begin or begin_parent
3. the page name (without leading or trailing spaces or tabs)
4. the group name (with leading and trailing spaces and tabs)

.. literalinclude:: ../../xrst/pattern.py
   :lines: 33-35
   :language: py

.. index:: code

.. _xrst.pattern@code:

code
****
Pattern for code command.

0. the entire line for the command with newline at front.
1. the indent for the command (spaces and tabs)
2. is the command with or without characters in front
3. This is the non space characters after the indent and before
   command (or None)
4. the language argument which is empty (just white space)
   for the second code command in each pair.
5. the line number for this line; see pattern['line'] above.

.. literalinclude:: ../../xrst/pattern.py
   :lines: 52-55
   :language: py

.. index:: comment_ch

.. _xrst.pattern@comment_ch:

comment_ch
**********
Pattern for comment_ch command

1. empty or character before command + the command
2. is the character (matched as any number of not space, tab or }

.. literalinclude:: ../../xrst/pattern.py
   :lines: 66-68
   :language: py

.. index:: dir

.. _xrst.pattern@dir:

dir
***
Pattern for dir command

1. Is either empty of character before command
2. Is the file_name in the command

.. literalinclude:: ../../xrst/pattern.py
   :lines: 79-82
   :language: py

.. index:: end

.. _xrst.pattern@end:

end
***
Pattern for end command

0. preceding character + white space + the command.
1. the page name.

.. literalinclude:: ../../xrst/pattern.py
   :lines: 93-93
   :language: py

.. index:: line

.. _xrst.pattern@line:

line
****
Pattern for line numbers are added to the input by add_line_number

0. the line command.
1. the line_number.

.. literalinclude:: ../../xrst/pattern.py
   :lines: 105-105
   :language: py

.. index:: literal

.. _xrst.pattern@literal:

literal
*******
Pattern for the literal command. Groups 1 and 2 will be None for this
pattern if {xrst_literal} is matched.

0. preceding character + the command.
1. characters, not including line number or command name, on first line.
2. rest of command, not including first \\n or final }.

.. literalinclude:: ../../xrst/pattern.py
   :lines: 118-120
   :language: py

.. index:: template_begin

.. _xrst.pattern@template_begin:

template_begin
**************
0. @{xrst_template_begin@ *template_file* @ *page_line* @}
1. *template_file*
2. *page_line*

.. literalinclude:: ../../xrst/pattern.py
   :lines: 129-132
   :language: py

.. index:: template_end

.. _xrst.pattern@template_end:

template_end
************
0. @{xrst_template_end@

.. literalinclude:: ../../xrst/pattern.py
   :lines: 139-140
   :language: py

.. index:: toc

.. _xrst.pattern@toc:

toc
***
Patterns for the toc_hidden, toc_list, and toc_table commands.

0. preceding character + the command.
1. command name; i.e., hidden, list, or table
2. the rest of the command that comes after the command name.
   This is an option order (on same line) followed by
   a list of file names with one name per line.
   The } at the end of the command is not included.
   This pattern may be empty.

If you change this pattern, check pattern_toc in process_children.py

.. literalinclude:: ../../xrst/pattern.py
   :lines: 157-159
   :language: py
