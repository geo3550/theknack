# -*- coding: utf-8 -*-

import knack_tools as kt
import os
from datetime import date


name = "Get Schedules"

## Default textbox width is 60 characters.
## To keep text from wrapping, it's best to keep
## lines shorter than that.
description = \
"""
This script processes the class schedule information 
released by the Registrar's Office and, for the people 
it can find (the information is usually incomplete), 
retrieves:
  - The class they're teaching
  - The time(s)
  - The location

Notes:

  - The raw schedule data can be found at:

      https://ro.umich.edu/calendars/schedule-of-classes

  - Currently, the script must be updated to point to the 
    correct data file by changing the "RO_DATA" variable 
    at the top of the file.

  - In order to export this information, add the following 
    to the "Custom Entry" box on the right side of the GUI:

      Schedule
"""

# Raw data from Registrar's Office
RO_DATA  = os.getcwd()+'/data/'+'ro_schedule_FA2018.csv'

# File to export all failed matches
ERROR_FILE = os.getcwd()+'/results/'+'scraper_errors.csv'


def processing_function(raw):
    """
    This is the top-level function for processing data.
    
    The function is meant to be passed to the importer (in this case GuiIO).
    The importer will call this function after it has parsed the raw data.
    """
    kdata = raw

    # import Registrar's Office Schedule information
    sdata = kt.importrosched(RO_DATA)

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

        # Format result for output
        # print(person['Individual'])
        hr_schedules = make_human_readable(schedules)
        # for s in hr_schedules:
        #     print(s)
        # print('\n')

        # Add to output data
        kdata[umid]['Schedule'] = '\n'.join(hr_schedules)

    print('Number of failures: '+str(len(errors)))
    kt.writecsv_summary(errors, ERROR_FILE)

    return kdata



def choose_schedule(person,schedules):
    """
    Given a list of possible schedules, and a person from knack,
    return the of schedules that are most likely for that person.
    """
    dept_codes = kt.DEPT_TO_DEPTCODES[ person['Department'] ]
    if person['Name: Last']=='Sanci':
        print(dept_codes)
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
