# -*- coding: utf-8 -*-

import knack_tools as kt
import mcomm_tools as mcomm
import requests
import os, time



name = "Scrape Enrollment"

## Default textbox width is 60 characters.
## To keep text from wrapping, it's best to keep
## lines shorter than that.
description = \
"""
This script uses MCommunity to determine who has graudated.

To export this information, choose the "Employment Status"
option on the right side of the GUI.
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
    global data_
    global newdata
    global person
    global query
    data_ = data
    newdata = data
    numremaining = len(data)
    errors = []
    ids = data.keys()
    tracker = len(ids)
    # get uniqnames
    print "Getting affiliations ..."

    for umid in ids:
        if not tracker%10:
            print "\tnumremaining: %d" % tracker
        # Don't do anything if person is already listed as retired
        if newdata[umid]['Employment Status'] == 'Retired':
            tracker -= 1
            continue
        query = data[umid]['Name: First']+" "+data[umid]['Name: Last']
        result = mc.querydb(query)
        if result:
            person, score = mc.choose_person(result,data[umid])
            if person:
                # check affiliation
                try:
                    if person['affiliation']=='Alumni':
                        newdata[umid]['Employment Status'] = 'Retired'
                except KeyError:
                    errors.append( (query, 'No Affiliation: '+query) )
                    print(errors[-1][1])
                    # print(person)

            else:
                errors.append( (query, "Can't choose person: "+query) )
                print(errors[-1][1])
                # print(query)
                # print(score)
        else:
            errors.append( (query, "Query Failed: "+query) )
            print(errors[-1][1])
        tracker -= 1
        time.sleep(.01)

    kt.writecsv_summary(errors, ERROR_FILE)

    return newdata
