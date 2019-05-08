.. knack_scripts documentation master file, created by
   sphinx-quickstart on Mon May  6 13:23:33 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.



.. toctree::
   :maxdepth: 2
   :caption: Contents:

This toolbox is an attempt to make processing data from AFT's Knack Database more powerful, repeatable, and easy. It is a GUI platform for making and using custom scipts to process Knack data by modifying the data itself and/or summarizing certain aspects of the data (such as membership %).


The GUI
=======

This scripting platform is meant to be started by running ``scripting_gui.py``. This brings up a GUI in which you can select which script to run (``Script``), what data to run it on (``Input Data``), and where to put the post-processed data (``Output Data``). The checkboxes on the right select which columns will be included in the ``Output Data`` file.

Input files are CSV (Comma Separated Value) files exported directly from any Knack people search. It must contain, at minimum, the ``Employer ID`` column, since this is how individual people are identified. Output files are also CSV files and will always contain the ``UMID`` column (same as ``Employer ID``).


Custom Scripts
==============

Any python files placed into the ``scripts`` directory will be treated as a custom script and imported for use. In order for this file to be used as a custom script, it must include:

1. A text variable called ``name``
2. A text variable called ``description``
3. A function (that takes 1 argument) called ``processing_function``	

If the import is successful, the text in the ``name`` variable will appear in the ``Script`` drop-down on the GUI and the ``description`` will appear in the description textbox. If the import is not successful, the error can be read from the terminal and the script will be ignored.

Writing a Custom Script
-----------------------

The ``processing_function`` gets a variable containing all the parsed data from the knack source file given by the user (in the ``Input Data`` textbox). This data is organized as follows:

The outer level is a dictionary, each key is a UMID (as a string).

Corresponding to each UMID is another dictionary of every column
in the input file (except "Employer ID"). For example::

	data = {
	  '93819370': {'Name: First':'Foo',   'Name: Last':'Bar'},
	  '83927489': {'Name: First':'Josie', 'Name: Last':'Cat'}
	}


By returning another variable with this same data structure (presumably some sort of processed data), that data will be written to the file given by the ``Output File`` textbox. If you return ``None``, no file will be written. You may also write to another file inside the function itself (often used to make a summary of measurements like membership % or to send a list of any processing errors to a separate file).

Please see ``example.py`` for a simple example of a custom script.


The 'knack_tools' Package
=========================

``knack_tools`` is a collection of useful tools for working with Knack data. There are lots of pre-written processing and file I/O functions along with other useful things like lists of umich department names.

For an overview of the more important tools, see :ref:`ktoverview`. For more complete documentation, see :ref:`ktref`.



The 'mcomm_tools' Package
=========================

``mcomm_tools`` contains the tools necessary to scrape data from Mcommunity. In it, there is a class called ``Scraper`` that can be used to do Mcommunity searches and to parse the data returned by the server.

See :ref:`mcomm` for complete documentation.



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
