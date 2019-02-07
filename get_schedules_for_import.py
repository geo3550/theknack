#!/bin/python2

import knack_tools as kt
import os
from datetime import date


# Defines columns to write to output file. Must match input file's header.
# Note: Since UMID is the db's key, it automatically exports as the 
# first column.
export_header = ['Name: First', 'Name: Last', 'Department',
            'Schedule - Course Title', 'Schedule - Time',
            'Schedule - Term', 'Schedule - Component', 'Schedule - Days',
            # 'Schedule - S', 'Schedule - M', 'Schedule - T', 'Schedule - W',
            # 'Schedule - TH', 'Schedule - F', 'Schedule - SU',
            'Schedule - Catalog Nbr', 
            'Schedule - Subject', 'Schedule - Location',
            'Schedule - Start Date', 'Schedule - End Date', 
            'Schedule - Session', 'Schedule - Codes', 
            'Schedule - Acad Group', 'Schedule - Class Nbr'
    ]

# Defines which department to look at.
depts    = ['3550.LSA - Romance Languages & Literatures']
# depts    = ['3550.COE - Electrical & Computer Engineering (ECE)']

# Relative paths are tricky sometimes; better to use full paths
INPATH  = os.getcwd()+'/data/'
OUTPATH = os.getcwd()+'/results/'

# Threshold date for "new hires"
NEW_HIRE_DATE = date(2017,05,01) # (year,month,day)




def data_processor(raw):
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
    sdata = kt.importrosched(INPATH+'ro_schedule_FA2018.csv')

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
    kt.writecsv_summary(errors, OUTPATH+'schedule_errors.csv')

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

# Create & run GUI (must be @ end of file)
# gui = kt.GuiIO(data_processor, export_header)
gui = kt.AutomaticIO(INPATH+'all_actives-9-24-18.csv', data_processor, 
                        export_header, OUTPATH+'sched_out.csv')
gui.master.title("sandbox")
gui.mainloop()  
