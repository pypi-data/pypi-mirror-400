.. _user-guide-name:

!!!!!!!!!!
user-guide
!!!!!!!!!!

.. meta::
   :keywords: user-guide,extract,sphinx,rst,files,license,git,repository,versions,install,stable,version,testing,from,source,dependencies,run,program,contents

.. index:: user-guide, extract, sphinx, rst, files

.. _user-guide-title:

Extract Sphinx RST Files
########################
This is a sphinx wrapper that extracts RST file from source code
and then runs sphinx to obtain html, tex, or pdf output files.
It includes automatic processing and commands that make sphinx easier to use.

.. contents::
   :local:

.. index:: license

.. _user-guide@License:

License
*******
`GPL-3.0-or-later <https://spdx.org/licenses/GPL-3.0-or-later.html>`_

.. index:: git, repository

.. _user-guide@Git Repository:

Git Repository
**************
`<https://github.com/bradbell/xrst>`_

.. index:: versions

.. _user-guide@Versions:

Versions
********

.. list-table::
   :widths: auto

   * - This version
     - xrst-2026.0.0
   * - Documentation for latest version
     - `latest <https://xrst.readthedocs.io/latest>`_
   * - Documentation for most recent stable version
     - `stable-2026 <https://xrst.readthedocs.io/stable-2026>`_
   * - Most recent release of this stable version
     - `release-2026 <https://codeload.github.com/bradbell/xrst/tar.gz/refs/tags/2026.0.0>`_

.. index:: install, stable, version

.. _user-guide@Install Stable Version:

Install Stable Version
**********************
Features in stable-2026 were frozen at the beginning of
the year and only includes bug fixed after that.
::

   pip install xrst

.. index:: install, testing, version

.. _user-guide@Install Testing Version:

Install Testing Version
***********************
Search for ``xrst`` on `test.pypi <https://test.pypi.org>`_
to determine the date corresponding to this version.
This installs the xrst dependencies and then replaces xrst
by its most recent test version::

   pip install xrst
   pip uninstall -y xrst
   pip install --index-url https://test.pypi.org/simple/ xrst

.. index:: install, from, source

.. _user-guide@Install From Source:

Install From Source
*******************
The following commands will download, test, build, and install
the current version from the master branch.
::

   git clone https://github.com/bradbell/xrst.git xrst.git
   cd xrst.git
   pytest -s pytest
   pip install .

You can determine the date corresponding to a version of the source code
using the following command:
::

   grep '^version *=' pyproject.toml

.. index:: dependencies

.. _user-guide@Dependencies:

Dependencies
************
The following is a list of the projects that xrst depends on
(and should be automatically installed by pip when you install xrst):

.. literalinclude:: ../../pyproject.toml
   :lines: 31-38
   :language: toml

.. index:: run, program

.. _user-guide@Run Program:

Run Program
***********
:ref:`run_xrst-title`

.. index:: contents

.. _user-guide@Contents:

Contents
********

-  :ref:`config_file-title`
-  :ref:`run_xrst-title`
-  :ref:`commands-title`
-  :ref:`automatic-title`
-  :ref:`wish_list-title`

.. toctree::
   :maxdepth: 1
   :hidden:

   config_file
   run_xrst
   commands
   automatic
   wish_list
