#!/bin/python2

import knack_tools as kt
import os
from datetime import date


# Defines columns to write to output file. Must match input file's header.
# Note: Since UMID is the db's key, it automatically exports as the 
# first column.
export_header = [   'Name: First', 'Name: Last', 'Department', 'Job Title',
                    'Assessment', 'Last Assessment Date', 'Hire Date', 
                    'FTE', 'Building','Office #', 'Schedule']

# Relative paths are tricky sometimes; better to use full paths
INPATH  = os.getcwd()+'/data/'
OUTPATH = os.getcwd()+'/results/'

# Threshold date for "new hires"
NEW_HIRE_DATE = date(2017,5,1) # (year,month,day)




def data_processor(raw):
    """
    This is the top-level function for processing data.
    
    The function is meant to be passed to the importer (in this case GuiIO).
    The importer will call this function after it has parsed the raw data.
    """
    global sdata

    # Only work with small group for now...
    # actives     = kt.filterdata(raw, kt.selectors.allactives)
    # kdata       = kt.filterdata(
    #             actives,
    #             lambda person: kt.selectors.bydept(person,depts)
    #         )

    actives     = kt.filterdata(raw, kt.selectors.allactives)
    # unit        = kt.filterdata(actives, kt.selectors.engineers)
    unit        = kt.filterdata(actives, kt.selectors.northcampus)
    nonpayers   = kt.filterdata(unit, kt.selectors.nonpayers)
    kdata       = kt.filterdata(
                nonpayers, 
                lambda person: kt.selectors.hiredafter(person,NEW_HIRE_DATE)
            )

    # import Registrar's Office Schedule information
    sdata = kt.importrosched(INPATH+'ro_schedule_WN2018.csv')

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
    kt.writecsv_summary(errors, OUTPATH+'nc_recent_errors.csv')

    return kdata



def choose_schedule(person,schedules):
    """
    Given a list of possible schedules, and a person from knack,
    return the of schedules that are most likely for that person.
    """
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

# Create & run GUI (must be @ end of file)
# gui = kt.GuiIO(data_processor, export_header)
gui = kt.AutomaticIO(INPATH+'all_actives-2-17-18.csv', data_processor, 
                        export_header, OUTPATH+'nc_recent_out.csv')
gui.master.title("sandbox")
gui.mainloop()  
