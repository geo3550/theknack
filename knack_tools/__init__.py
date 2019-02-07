# -*- coding: utf-8 -*-

"""
knack_tools.py
v0.2

This is a library of tools that can be used to more easily 
& consistently work with data from Knack.

'data' organization:
    The outer level is a dictionary, each key is a UMID (as a string).

    Corresponding to each UMID is another dictionary of every column
    in the input file (except "Employer ID"). For example:

    data = {
      '93819370': {'Name: First':'Foo', 'Name: Last':'Bar'},
      '83927489': {'Name: First':'Josie', 'Name: Last':'Cat'}
    }

""" 


from Tkinter import *
import tkFileDialog
import json
import unicodecsv as csv
# import csv
import os, time
from io import BytesIO
from copy import copy



# local modules
import selectors
from constants import *





###############################################################################
# Data Processing Functions
###############################################################################


def count_duespayers(data):
    ii = 0
    for p in data.values():
        if p['Member Status'] == 'Union Dues': ii += 1
    return ii

def count_nonpayers(data):
    ii = 0
    for p in data:
        if p['Member Status'] == 'Non-Payer': ii += 1
    return ii







###############################################################################
# File I/O
###############################################################################

def filterdata(data, selector_fn):
    """
    Given a dictionary of people, call 'selector_fn' for each person      
    and remove any entries that return 'None'
    """
    # First, decide whether or not to keep each row
    data = {id: selector_fn(data[id]) for id in data.keys()}

    # Then, remove the entries left empty by 'selector_fn'
    filtered_data = dict((k, v) for k, v in data.iteritems() if v)

    return filtered_data

 
def parsebyid(lines):
    """
    Given raw data, parse each line into a dictionary representing
    that person's data, then return a dictionary of each person,
    using UMIDs as the keys.
    """

    # Sanitize column labels and find the UMID column
    header = [elt.strip() for elt in lines[0]]
    id_index = header.index('Employee ID')

    # Remove '3550' prefix from everything
    for idx, line in enumerate(lines[1:]):
        lines[idx] = [remove_prefix(elt,'3550.') for elt in line]

    # Create dictionary for each person
    keys = header
    del keys[id_index]
    ids = []
    data = []
    for line in lines[1:]:
        ids = ids+[ line[id_index] ]
        del line[id_index]

        datum = dict(zip(keys,line))
        data = data+[ datum ]

    # Create overall dictionary of all the people
    # We end up with this structure:
    # data{umid}{column_label} => data for specific person.
    return [dict(zip(ids,data)), header, ids]


def remove_prefix(s,prefix):
    return s[len(prefix):] if s.startswith(prefix) else s

 
def parsestews(lines):
    """
    Given raw export of stews list,
    parse each line into a dictionary with departments as keys
    and a list of stewards' names as values.
    """

    # Sanitize column labels and find the Depatment column
    header = [elt.strip() for elt in lines[0]]

    # There's actually 2 "Department" columns in the Stewards list
    dept_index = [ii for ii, h in enumerate(header) if h=='Department'][-1]
    name_index = header.index('Name')

    # Create unduplicated list of all stewarded departments
    depts = list({line[dept_index] for line in lines[1:]})
    # Initialize dictionary with empty lists for each departmet
    stews = dict(zip(depts,[[]]*len(depts)))

    for line in lines[1:]:
        if not line[dept_index]:
            continue
        stews[line[dept_index]] = stews[line[dept_index]] + [line[name_index]]

    # Remove unassigned stewards (these are typ. ex-stews)
    del stews['']

    return stews


def parserosched(lines):
    """
    Given raw export of registrar's office schedule 
    (found at: http://ro.umich.edu/schedule/), parse each line
    into a dictionary with instructor of the form:
        {last_name: [row_data0 row_data1 ...]}
    where each 'row_data' represents a row with the same instructor
    last name and is encoded as a dictionary of the form:
        {column label: data}
    """

    # Sanitize column labels and find the Instructor column
    header = [elt.strip() for elt in lines[0]]
    lname_index = header.index('Instructor')

    # Parse the Instructor column
    lnames_byrow = []
    for line in lines[1:]:
        lnames_byrow = lnames_byrow + [line[lname_index].split(', ')]

    # Create unduplicated list of all instructors
    lnames = []
    for row in lnames_byrow:
        lnames = lnames + row
    lnames = list(set(lnames))

    # Initialize dictionary with empty lists for each last name
    d = dict(zip(lnames,[[]]*len(lnames)))
    # ...and the dictionary for an empty row
    column_labels = lines[0]; column_labels.pop(lname_index)
    mtrow = dict(zip(column_labels,[[]]*len(column_labels)))

    # Extract each line & assign it to the appropriate name
    for r, line in enumerate(lines[1:]):
        if not line[lname_index]:
            continue

        row_dict = copy(mtrow)
        for c, clabel in enumerate(column_labels):
            row_dict[clabel] = line[c]
        for name in lnames_byrow[r]:
            d[name] = d[name] + [row_dict]

    return d 



def importstews(filename):
    # Read in file
    lines = _readcsv(filename)

    # Process raw data
    data = parsestews(lines)
    return data


def importrosched(filename):
    # Read in file
    lines = _readcsv(filename)

    # Process raw data
    data = parserosched(lines)
    return data


def importcsv(filename):
    print "Processing data ..."
    # Read in file
    lines = _readcsv(filename)

    # Process raw data
    data, header, ids = parsebyid(lines)
    return data 


def _readcsv(filename):
    dirname = os.path.dirname(filename)
    os.chdir(dirname)

    with open(filename, "rb") as f:
        csvreader = csv.reader(f, encoding='utf-8-sig')
        lines = [line for line in csvreader]
    f.close()

    # No idea why csvreader isn't removing the quotes in first cell...
    lines[0][0] = lines[0][0].strip('"')
    return lines


def writecsv_byid(data_to_write, export_header, filename):
    if not export_header:
        return
    if export_header == 'all fields':
        ids = data_to_write.keys()
        export_header = data_to_write[ids[0]].keys()


    print "Writing data ..."
    with open(filename, "wb") as f:
        csvwriter = csv.writer(f)
        csvwriter.writerow(['UMID']+export_header)
        for id in data_to_write.keys():
            try:
                row = [data_to_write[id][col] for col in export_header]
            except KeyError:
                print(id)
                print(data_to_write[id])
                raise
            csvwriter.writerow([id]+row)
    f.close()



def writecsv_summary(data_to_write, filename):
    print "Writing summary ..."
    with open(filename, "wb") as f:
        csvwriter = csv.writer(f)
        for row in data_to_write:
            csvwriter.writerow(row)
    f.close()






###############################################################################
# Importers/Exporters
###############################################################################

class GuiIO(Frame):
    """Creates GUI for importing, processing, and exporting Knack data.""" 
    def __init__(   self, processing_fn, export_header, 
                    out_filename='./out.csv', master=None   ):
        Frame.__init__(self, master)
        self.status = StringVar()
        self.filename = StringVar()
        self.createWidgets()
        self.grid()
        self.processing_fn = processing_fn
        self.export_header = export_header
        self.out_filename = out_filename
    def createWidgets(self):
        #self.tokenprompt = Label(text = "Access token:")
        #self.tokenentry = Entry()
        self.filebutton = Button(   self, text="Select Input File",
                                    command=self.getfilename    )
        self.filenameprompt = Label(textvariable = self.filename)
        self.getunbutton = Button(  self, text="Process File!", 
                                    command=self.process )
        self.statusprompt = Label(textvariable = self.status)

        #self.tokenprompt.grid(row=0, column=0)
        #self.tokenentry.grid(row=0, column=1)
        self.filenameprompt.grid(row=1, column=0, columnspan=2)
        self.filebutton.grid(row=2, column=0)
        self.getunbutton.grid(row=3, column=0)
        self.statusprompt.grid(row=3, column=1)
    def getfilename(self):
        self.filename.set(tkFileDialog.askopenfilename())
    def process(self):
        self.status.set("Processing ...")

        # Read in file
        data = importcsv(self.filename.get())
        # Run processing function on data
        processed_data = self.processing_fn(data)
        # Write processed data
        writecsv_byid(processed_data, self.export_header, self.out_filename)

        self.status.set("Done!")


class AutomaticIO():
    """Imports, processes, and exports Knack data from given file.""" 
    class m:
        """Dummy class to make the interface similar to GuiIO"""
        def title(self,txt): pass


    def __init__(   self, in_filename, processing_fn, export_header, 
                    out_filename='out.csv', master=None  ):
        print(os.getcwd())
        self.filename = in_filename
        self.out_filename = out_filename
        self.processing_fn = processing_fn
        self.export_header = export_header
        self.master = self.m()


    def mainloop(self):
        # Read in file
        data = importcsv(self.filename)
        _data = data
        # Run processing function on data
        processed_data = self.processing_fn(data)
        # Write processed data
        writecsv_byid(processed_data, self.export_header, self.out_filename)
  
