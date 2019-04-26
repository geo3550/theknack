# -*- coding: utf-8 -*-

import knack_tools as kt


name = "Scripting Example"

## Default textbox width is 60 characters.
## To keep text from wrapping, it's best to keep
## lines shorter than that.
description = \
"""
This is a simple example for writing your own script.
"""

# Defines which department to look at.
depts = ['Urban Planning', 'Biological Chemistry Dept']


def processing_function(data):
    """
    This is the top-level function for processing data.
    
    The function is meant to be passed to the importer (in this case GuiIO).
    The importer will call this function after it has parsed the raw data.
    """

    # Do some processing
    #   Note that there are lots of pre-written selectors in the
    #   "knack_tools" package. For example, you could replace
    #   "custom_row_selector" with "kt.selectors.all_actives"
    #   to get only people currently in the bargaining unit.
    processed = kt.filterdata(data, custom_row_selector)

    # Summarize some results & show it on the command prompt
    nm = kt.count_duespayers(processed)
    membership = nm/float(len(processed))
    print('\n')
    print('Membership in selected departments: %d%%' % (membership*100))
    print('\n')

    # Return the processed data 
    return processed



def custom_row_selector(row):
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


