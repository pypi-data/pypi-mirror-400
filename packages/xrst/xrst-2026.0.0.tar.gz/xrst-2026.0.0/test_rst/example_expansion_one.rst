.. _example_expansion_one-name:

!!!!!!!!!!!!!!!!!!!!!
example_expansion_one
!!!!!!!!!!!!!!!!!!!!!

.. meta::
   :keywords: example_expansion_one,first,expansion,number,spelling,paragraph,third,this,template,file,usage



.. index:: example_expansion_one, first, expansion

.. _example_expansion_one-title:

First Expansion
###############

.. contents::
   :local:

.. index:: expansion, number

.. _example_expansion_one@Expansion Number:

Expansion Number
****************
This is expansion number one of the template file
``example/template_file.xrst`` .

.. index:: spelling

.. _example_expansion_one@Spelling:

Spelling
********
Template files can not have :ref:`spell commands<spell_example-name>` .
Every page that uses a template file will have to include
the template file special words it the page's spell command.
You can avoid this by surrounding the intended use of special words,
and double words, by
``{xrst_spell_off}`` and ``{xrst_spell_on}`` .
This is what is done in the following sentence:
Using 'myspecialword' and using 'double double' are OK here.

.. index:: first, paragraph

.. _example_expansion_one@First Paragraph:

First Paragraph
***************
This paragraph is displayed if the case argument is first.

.. index:: third, paragraph

.. _example_expansion_one@Third Paragraph:

Third Paragraph
***************
This paragraph is displayed if the case argument is not third.

.. index:: template

.. _example_expansion_one@This Template File:

This Template File
******************

.. literalinclude:: ../../example/template_file.xrst
   :language: rst

.. index:: template, usage

.. _example_expansion_one@This Template Usage:

This Template Usage
*******************

.. literalinclude:: ../../example/template.xrst
   :lines: 23-29
   :language: rst


