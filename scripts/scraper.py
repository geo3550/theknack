#!/bin/python2

import knack_tools as kt
import mcomm_tools as mcomm
import requests
import os, time


name = "MCommunity Scraper"

## Default textbox width is 60 characters.
## To keep text from wrapping, it's best to keep
## lines shorter than that.
description = \
"""
This script retrieves the following information from 
MCommunity:
  - Employer Unique Name
  - Enrolled Department
  - Degree

To export this data, copy and paste the following into 
"Custom Entry" on the right side of the GUI:

Employer Unique Name,Enrolled Deptartment,Degree
"""


# Create M-Community Object
mc = mcomm.Scraper()

# File to export all failed matches
ERROR_FILE = os.getcwd()+'/results/'+'scraper_errors.csv'



def processing_function(data):
    """
    This is the top-level function for processing data.
    
    The function is meant to be passed to the importer (in this case GuiIO).
    The importer will call this function after it has parsed the raw data.
    """
    newdata = data
    numremaining = len(data)
    errors = []
    ids = data.keys()
    tracker = len(ids)
    # get uniqnames
    print "Getting uniqnames ..."

    for umid in ids:
        if not tracker%10:
            print "\tnumremaining: %d" % tracker
        # Don't do anything if person has uniqname already
        if newdata[umid]['Employer Unique Name'] and newdata[umid]['Secondary Email'] and \
           newdata[umid]['Secondary Department']  and newdata[umid]['Education']:
            # Don't forget to add the new columns
            newdata[umid]['Enrolled Department'] = newdata[umid]['Secondary Department']
            newdata[umid]['Degree'] = newdata[umid]['Education']
            tracker -= 1
            continue
        query = data[umid]['Name: First']+" "+data[umid]['Name: Last']
        result = mc.querydb(query)
        if result:
            person, score = mc.choose_person(result,data[umid])
            if person:
                # uniqname & email
                try:
                    uniq = person['uniqname']
                    newdata[umid]['Employer Unique Name'] = uniq
                    newdata[umid]['Secondary Email'] = uniq+"@umich.edu"
                except KeyError:
                    errors.append( (query, 'No Uniqname: '+query) )
                    print(errors[-1][1])

                # enrolled department
                enrolled_dept, degree = mc.getenrolled(person)
                newdata[umid]['Enrolled Department'] = enrolled_dept
                newdata[umid]['Degree'] = degree

            else:
                # Don't forget to add the new columns
                newdata[umid]['Enrolled Department'] = ''
                newdata[umid]['Degree'] = ''
                errors.append( (query, "Can't choose person: "+query) )
                print(errors[-1][1])
                # print(query)
                # print(score)
        else:
            # Don't forget to add the new columns
            newdata[umid]['Enrolled Department'] = ''
            newdata[umid]['Degree'] = ''
            errors.append( (query, "Query Failed: "+query) )
            print(errors[-1][1])
        tracker -= 1
        time.sleep(.01)

    kt.writecsv_summary(errors, ERROR_FILE)

    return newdata
