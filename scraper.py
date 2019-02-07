#!/bin/python2

import knack_tools as kt
import requests
import os, time


# Defines columns to write to output file. Must match input file's header.
# Note: Since UMID is the db's key, it automatically exports as the 
# first column.
# If export_header == 'all fields', it will export the entire DB.
export_header = [
                    'Name: First', 'Name: Last', 'Email', 'Employer Unique Name',
                    'Enrolled Department', 'Degree'
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
        query = data[umid]['Name: First']+" "+data[umid]['Name: Last']
        result = mc.querydb(query)
        if result:
            person, score = mc.choose_person(result,data[umid])
            if person:
                # uniqname & email
                try:
                    uniq = person['uniqname']
                    newdata[umid]['Employer Unique Name'] = uniq
                    newdata[umid]['Email'] = uniq+"@umich.edu"
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
        time.sleep(.1)

    kt.writecsv_summary(errors, OUTPATH+'scraper_errors.csv')

    return newdata


# Create M-Community Object
mc = kt.Scraper()

# Create & run GUI (must be @ end of file)
# gui = kt.GuiIO(data_processor, export_header, OUTPATH+'scraper_out.csv')
gui = kt.AutomaticIO(INPATH+'all_nonactives-11-7-18.csv', data_processor, 
                        export_header, OUTPATH+'scraper_out.csv')
gui.master.title("GEO Scrape-o-Matic")
gui.mainloop()  
