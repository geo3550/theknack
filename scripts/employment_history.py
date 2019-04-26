# -*- coding: utf-8 -*-

import knack_tools as kt


import os
from copy import deepcopy
from datetime import date


name = "Employment History"

## Default textbox width is 60 characters.
## To keep text from wrapping, it's best to keep
## lines shorter than that.
description = \
"""
This script looks at who has been teaching for 1 year,
2 years, etc. and summarizes the membership % in each
cohort.
"""


###############################################################################
# Helper Functions
###############################################################################
def str_2col(text1,text2,tabwidth):
    TAB = tabwidth-len(text1)
    if TAB<1: TAB = 1
    return text1 + ' '*TAB + text2


###############################################################################
# Main script
###############################################################################
def processing_function(data):
    """
    This is the top-level function for processing data.
    
    The function is meant to be passed to the importer (in this case GuiIO).
    The importer will call this function after it has parsed the raw data.
    """
    actives = kt.filterdata(data, kt.selectors.allactives)


    termcount_total = {}
    termcount_members = {}
    for umid in actives:
        person = actives[umid]

        # Process 'Employment Period' Field
        termcount = len(person['Employment Period'].split(', '))
        person['Term Count'] = termcount
        
        # Count Total # for each term count
        try:
            termcount_total[termcount] = termcount_total[termcount] + 1
        except KeyError:
            termcount_total[termcount] = 1
        
        # Count # of members for each term count
        if person['Member Status'] == 'Union Dues':
            try:
                termcount_members[termcount] = termcount_members[termcount] + 1
            except KeyError:
                termcount_members[termcount] = 1
        else:
            if not termcount in termcount_members:
                termcount_members[termcount] = 0


    # Summarize
    membership = {}
    for termcount in termcount_total.keys():
        membership[termcount] = termcount_members[termcount] / \
                                    float(termcount_total[termcount])

        print(str(termcount) + ' Terms Taught:')
        print(str_2col('Total Count:',str(termcount_total[termcount]),30))
        print(str_2col('Membership:', str(membership[termcount]*100)+' %',30))
        print('\n')

    return None