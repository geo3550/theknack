.. _ktoverview:

'knack\_tools' Overview
=====================================

``knack_tools`` is a collection of useful tools for working with Knack data. There are lots of pre-written processing and file I/O functions along with other useful things like lists of umich department names.

The following is a collection of the most useful features. For more complete documentation, see :ref:`ktref`.



Processing Functions
--------------------

.. autofunction:: knack_tools.filterdata

.. autofunction:: knack_tools.count_duespayers

.. autofunction:: knack_tools.count_nonpayers



The knack_tools.selectors Module
--------------------------------

This module contains all the pre-written functions to be used by the ``knack_tools.filterdata`` function. In general, they take one argument (the dictionary for a single person's data), and return either that same data (if the person is to be included in the output data) or ``None`` (if the person is to be removed from the output data).

Sometimes, however, a function needs to accept more information than just the person's data. For example, the ``bydept`` selector must also know what department(s) to select for. In this case, a wrapper function must be created by the user in order to pass ``filterdata`` a function with only 1 input. You can use python's ``lambda`` function to do this::

    import knack_tools as kt

    ## "north_campus" will contain only people from North Campus Departments.
    north_campus = kt.filterdata(
                data,
                lambda person: kt.selectors.bydept(person,kt.constants.NORTH_CAMPUS_DEPTS)
            )

The following are the available selectors:

.. automodule:: knack_tools.selectors
    :members:



The knack_tools.constants Module
--------------------------------

This module contains information specific to Umich's data (such as department names).

.. automodule:: knack_tools.constants
	:members:



File I/O
--------

.. autofunction:: knack_tools.importcsv

.. autofunction:: knack_tools.importrosched

.. autofunction:: knack_tools.importstews

.. autofunction:: knack_tools.writecsv_byid

.. autofunction:: knack_tools.writecsv_summary

