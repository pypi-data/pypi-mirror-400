.. _code_cmd-name:

!!!!!!!!
code_cmd
!!!!!!!!

.. meta::
   :keywords: code_cmd,code,command,syntax,purpose,code-block,requirements,language,rest,of,line,spell,checking,example

.. index:: code_cmd, code

.. _code_cmd-title:

Code Command
############

.. contents::
   :local:

.. _code_cmd@Syntax:

Syntax
******
- ``{xrst_code`` *language* ``}``
- ``{xrst_code}``

.. _code_cmd@Purpose:

Purpose
*******
A code block, directly below in the current input file, begins (ends) with
a code command that contains *language* (not containing *language*).

.. index:: code-block

.. _code_cmd@code-block:

code-block
**********
This command is similar to the following sphinx directive

| |tab| .. code-block:: *language*
|
| |tab| |tab| Source code in the specified language

The xrst code command has the following difference:

#. Other characters on the same line as the code commands
   are not included in the rst output or the displayed source code.
   One can use these characters to end and begin comments so that the
   code also executes.
#. The source code does not need to be indented. This is especially useful
   with languages like python and rst where the indentation is used to
   begin and end sections of code.
#. The source code does not need to be surrounded by empty lines.

.. index:: requirements

.. _code_cmd@Requirements:

Requirements
************
Each code section ends with
a line containing the second version of the command; i.e., ``{xrst_code}``.
Hence there must be an even number of code commands.

.. index:: language

.. _code_cmd@language:

language
********
A *language* is a non-empty sequence of lower case letters.
It determines the language for highlighting the code block.

.. index:: rest, line

.. _code_cmd@Rest of Line:

Rest of Line
************
Other characters on the same line as a code commands
are not included in the xrst output.
This enables one to begin or end a comment block
without having the comment characters in the xrst output.

.. index:: spell, checking

.. _code_cmd@Spell Checking:

Spell Checking
**************
Code blocks as usually small and
spell checking is done for these code blocks.
You can turn off this spell checking by putting
:ref:`spell_cmd@spell_off` before and :ref:`spell_cmd@spell_on` after
a code block.
Spell checking is not done for code blocks included using the
:ref:`literal command<literal_cmd-name>` .

.. _code_cmd@Example:

Example
*******
:ref:`code_example-name`
