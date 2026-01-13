.. _get_conf_dict-name:

!!!!!!!!!!!!!
get_conf_dict
!!!!!!!!!!!!!

.. meta::
   :keywords: get_conf_dict,get,configuration,dictionary,prototype,config_file,conf_dict

.. index:: get_conf_dict, get, configuration, dictionary

.. _get_conf_dict-title:

Get Configuration Dictionary
############################
This routine is called before the current working directory is changed to
the *project_directory* (because it determines the project directory)
so it cannot use the xrst :ref:`system_exit-name` .

.. contents::
   :local:

.. index:: prototype

.. _get_conf_dict@Prototype:

Prototype
*********

.. literalinclude:: ../../xrst/get_conf_dict.py
   :lines: 509-511,709-711
   :language: py

.. index:: config_file

.. _get_conf_dict@config_file:

config_file
***********
is the location of the :ref:`run_xrst@config_file` specified on
the xrst command line.

.. index:: conf_dict

.. _get_conf_dict@conf_dict:

conf_dict
*********
is the python dictionary corresponding to the toml file with the defaults
filled in. All of the values in the dictionary have been check for
the proper type. This includes recursive checking; e.g. a list is checked
to make sure its elements have the proper type.
