# -*- coding: utf-8 -*-

import knack_tools as kt
import os
from datetime import date



name = "Get Schedules For Knack Import"

## Default textbox width is 60 characters.
## To keep text from wrapping, it's best to keep
## lines shorter than that.
description = \
"""
This is the same as "Get Schedules" except the ouput
is formatted to be imported into knack. To export the
data, copy the following into the "Custom Entry" box
on the right side of the GUI:


Schedule - Course Title,Schedule - Time,Schedule - Term,
Schedule - Component,Schedule - Days,Schedule - Catalog Nbr,
Schedule - Subject,Schedule - Location,Schedule - Start Date,
Schedule - End Date,Schedule - Session,Schedule - Codes,
Schedule - Acad Group,Schedule - Class Nbr
"""

# Raw data from Registrar's Office
RO_DATA_FILE  = os.getcwd()+'/data/'+'ro_schedule_FA2018.csv'

# File to export all failed matches
ERROR_FILE = os.getcwd()+'/results/'+'scraper_errors.csv'


def processing_function(raw):
    """
    This is the top-level function for processing data.
    
    The function is meant to be passed to the importer (in this case GuiIO).
    The importer will call this function after it has parsed the raw data.
    """
    global sdata

    # Only work with small group for now...
    actives     = kt.filterdata(raw, kt.selectors.allactives)
    # kdata       = kt.filterdata(
    #             actives,
    #             lambda person: kt.selectors.bydept(person,depts)
    #         )
    kdata = actives

    # actives     = kt.filterdata(raw, kt.selectors.allactives)
    # engin       = kt.filterdata(actives, kt.selectors.engineers)
    # kdata       = kt.filterdata(
    #             engin, 
    #             lambda person: kt.selectors.hiredafter(person,NEW_HIRE_DATE)
    #         )
    
    # import Registrar's Office Schedule information
    sdata = kt.importrosched(RO_DATA_FILE)

    # extract schedules for each person and add column to knack data
    errors = []
    for umid in kdata.keys():
        person = kdata[umid]
        lname = person['Name: Last']

        # Grab all schedules with this person's last name
        # (since that's the only info the registrar gives us)
        try:
            schedules = sdata[lname]
        except KeyError:
            TAB = 20-len(lname)
            if TAB<1: TAB = 1
            kdata[umid]['Schedule'] = ''
            msg = 'Failed to find:  \t"'+lname+'"'+' '*TAB+'in department: '+\
                    person['Department']
            errors.append([lname,msg])
            print(msg)
            continue

        # Choose most likely from all schedules with that last name
        schedules = choose_schedule(person,schedules)
        if not schedules:
            TAB = 20-len(lname)
            if TAB<1: TAB = 1
            kdata[umid]['Schedule'] = ''
            msg = 'Failed to choose:\t"'+lname+'"'+' '*TAB+'in department: '+\
                    person['Department']
            errors.append([lname,msg])
            print(msg)
            continue

        # Not sure how to deal with multiple results right now...
        if len(schedules)>1:
            TAB = 20-len(lname)
            if TAB<1: TAB = 1
            msg = 'Multiple schedules for:\t"'+lname+'"'+' '*TAB+'in department: '+\
                    person['Department']
            errors.append([lname,msg])
            continue

        # Add to output data
        s = schedules[0]
        days = ''.join([s['M'],s['T'],s['W'],s['TH'],s['F'],s['S'],s['SU']])
        kdata[umid]['Schedule - Days'] = days

        empty_cols = dict()
        empty_cols['Days'] = u''
        for col in schedules[0].keys():
            out_col = 'Schedule - '+col;
            kdata[umid][out_col] = schedules[0][col]
            empty_cols[out_col] = u''


    # Add empty entries for people that have been skipped
    for umid in kdata:
        if not 'Schedule - Course Title' in kdata[umid]:
            kdata[umid].update(empty_cols)


    # Don't output anyone we don't have schedule info for
    kdata_filtered = kt.filterdata(
                kdata,
                lambda person: kt.selectors.column_is_empty(person,'Schedule - Course Title')
            )

    print('Number of failures: '+str(len(errors)))
    kt.writecsv_summary(errors, ERROR_FILE)

    return kdata_filtered



def choose_schedule(person,schedules):
    """
    Given a list of possible schedules, and a person from knack,
    return the of schedules that are most likely for that person.
    """
    if not person['Department']:
        print(person)
    dept_codes = kt.DEPT_TO_DEPTCODES[ person['Department'] ]

    # Just naivly check the department for now
    out = []
    for s in schedules:
        if s['Component'] == 'IND':
            # Assume indep. studies are professors;
            # filters out some duplicate names without incurring
            # too many false negatives (hopefully)
            continue

        dcode = s['Subject'].split(' (')[1][:-1]
        if dcode in dept_codes:
            out.append(s)
    return out


def make_human_readable(schedules):
    """
    Given a list of schedules, output a list of strings of the form:
    'EECS 527 DIS: MWF 3-430PM @ 1012 EECS'
    """
    out = []
    for s in schedules:
        course  = s['Subject'].split(' (')[1][:-1] + \
                  s['Catalog Nbr']
        ctype   = s['Component']
        time    = s['Time']
        room    = s['Location']
        days = ''.join([s['M'],s['T'],s['W'],s['TH'],s['F'],s['S'],s['SU']])

        this_sched = course+' ' + ctype+': ' + days+' ' + time+' @ ' + room
        out.append(this_sched)

    return out
