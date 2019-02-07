#!/bin/python2

import knack_tools as kt


# Defines columns to write to output file. Must match input file's header.
# Note: Since UMID is the db's key, it automatically exports as the 
# first column.
export_header = ['Name: First', 'Name: Last', 'Department', 'Member Status']

# Defines which department to look at.
depts = ['Urban Planning', 'Biological Chemistry Dept']


def data_processor(data):
    """
    This is the top-level function for processing data.
    
    The function is meant to be passed to the importer (in this case GuiIO).
    The importer will call this function after it has parsed the raw data.
    """

    # Do some processing
    processed = kt.filterdata(data, row_selector)

    # Summarize some results
    nm = kt.count_duespayers(processed)
    membership = nm/float(len(processed))
    print('\n')
    print('Membership in selected departments: %d%%' % (membership*100))
    print('\n')

    return processed



def row_selector(row):
    """
    Given the dictionary for a single person, decide whether to
    pass the data or return None.
    """
    select_flag = False

    ##############################
    # Do whatever checks you want
    ##############################

    for d in kt.NORTH_CAMPUS_DEPTS:
        if row['Department'] == d:
            select_flag = True

    ##############################

    # Return
    if select_flag:
        return row
    else:
        return None



# Create & run GUI (must be @ end of file)
gui = kt.GuiIO(data_processor, export_header)
gui.master.title("sandbox")
gui.mainloop()  
