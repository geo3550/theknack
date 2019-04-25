#!/bin/python2

import knack_tools as kt
import mcomm_tools as mcomm
import requests
import os, time


# Defines columns to write to output file. Must match input file's header.
# Note: Since UMID is the db's key, it automatically exports as the 
# first column.
# If export_header == 'all fields', it will export the entire DB.
export_header = [
                    'Name: First', 'Name: Last', 'Employment Status'
                ]
# export_header = 'all fields'

# Relative paths are tricky sometimes; better to use full paths
INPATH  = os.getcwd()+'/data/'
OUTPATH = os.getcwd()+'/results/'



def data_processor(data):
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
                    print(person['affiliation'])
                    if person['affiliation']=='Alumni':
                        newdata[umid]['Employment Status'] = 'Retired'
                except KeyError:
                    errors.append( (query, 'No Affiliation: '+query) )
                    print(errors[-1][1])
                    print(person)

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

    kt.writecsv_summary(errors, OUTPATH+'scraper_errors.csv')

    return newdata





# Create M-Community Object
mc = mcomm.Scraper()

# Create & run GUI (must be @ end of file)
# gui = kt.GuiIO(data_processor, export_header, OUTPATH+'scraper_out.csv')
# gui = kt.AutomaticIO(INPATH+'all_inactives-2-18-19.csv', data_processor, 
gui = kt.AutomaticIO(INPATH+'all_fields-1.csv', data_processor, 
                        export_header, OUTPATH+'scraper_out.csv')
gui.master.title("GEO Scrape-o-Matic")
gui.mainloop()  
