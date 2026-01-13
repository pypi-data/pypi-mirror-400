.. _get_started-name:

!!!!!!!!!!!
get_started
!!!!!!!!!!!

.. meta::
   :keywords: get_started,title:,getting,started,heading:,steps,links,to,this,page,example,file

.. index:: get_started, title:, getting, started

.. _get_started-title:

Title: Getting Started
######################
The name of this page is ``get_started`` and its title is
``Title: Getting Started`` .
All of the headings below begin with ``Heading:`` .

.. contents::
   :local:

.. index:: heading:, steps

.. _get_started@Heading\: Steps:

Heading: Steps
**************

#. Use pip as follows to install the most recent stable version of xrst::

      pip install xrst

#. If you like, you can replace this by the most recent test version
   of xrst using the following commands::

      pip uninstall -y xrst
      pip install --index-url https://test.pypi.org/simple/ xrst

#. Create an empty directory and make it your current working directory.

#. Create an empty file called ``xrst.toml`` (the xrst configure file)
   in the working directory. The empty file tells xrst to use
   all its default configuration settings.

#. Create a file called ``project.xrst``, in the working directory,
   with the contents of
   :ref:`this example file<get_started@Heading: This Example File>` .
   Note that ``project.xrst`` is the default location for the xrst root file.
   You could change the location of the root file to  ``get_started.xrst``
   by entering the following in your ``xrst.toml`` file::

      [root_file]
      default = 'get_started.xrst'

#. Execute the following command::

      xrst

#. Use your web browser to open the file below
   (this file name is relative to your working directory)::

      build/html/get_started.html

#. You may have gotten spelling warnings for two reasons:

   #. The project dictionary for this example is empty while the one used
      to test xrst is not.
   #. You are using is different version of the spell checker
      from the one used to test xrst.

   You can fix these warning by adding or removing words in the
   spell command at the beginning of the get_started.xrst file.
   If you do this correctly and re-execute the xrst command,
   the spelling warnings should not appear.

#. You should have gotten a warning that none of the input_files commands
   succeeded. These commands are used to check if all the input files get used.
   You can remove this check by adding the text below at the end of your
   xrst.toml file::

      [input_files]
      data = [ ]

   If you then re-execute the xrst command, the input files
   warning should not appear.

.. index:: heading:, links, page

.. _get_started@Heading\: Links to this Page:

Heading: Links to this Page
***************************

- :ref:`get_started-name`

- :ref:`get_started-title`

- :ref:`get_started@Heading: Steps`

- :ref:`get_started@Heading: Links to this Page`

- :ref:`get_started@Heading: This Example File`

.. index:: heading:

.. _get_started@Heading\: This Example File:

Heading: This Example File
**************************
The file below demonstrates the use of
``xrst_begin``,  ``xrst_end``, ``xrst_spell``, ``xrst_literal``
and heading references :

.. literalinclude:: ../../example/get_started.xrst
   :language: rst
