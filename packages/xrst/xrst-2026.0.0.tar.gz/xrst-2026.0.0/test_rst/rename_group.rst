.. _rename_group-name:

!!!!!!!!!!!!
rename_group
!!!!!!!!!!!!

.. meta::
   :keywords: rename_group,rename,a,subset,of,group,tmp_dir,old_group_name,new_group_name,spell.toml,prototype

.. index:: rename_group, rename, subset, group

.. _rename_group-title:

Rename a Subset of a Group
##########################

.. contents::
   :local:

.. index:: tmp_dir

.. _rename_group@tmp_dir:

tmp_dir
*******
is the directory where spell.toml is located

.. index:: old_group_name

.. _rename_group@old_group_name:

old_group_name
**************
is the old name that we are replacing in the xrst begin commands.

.. index:: new_group_name

.. _rename_group@new_group_name:

new_group_name
**************
is the new name that we are using in the xrst begin commands.

.. index:: spell.toml

.. _rename_group@spell.toml:

spell.toml
**********
see :ref:`replace_spell@spell.toml` .

.. index:: prototype

.. _rename_group@Prototype:

Prototype
*********

.. literalinclude:: ../../xrst/rename_group.py
   :lines: 41-44
   :language: py
