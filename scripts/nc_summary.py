# -*- coding: utf-8 -*-

import knack_tools as kt
from datetime import date, datetime
import os


name = "North Campus Summary"

## Default textbox width is 60 characters.
## To keep text from wrapping, it's best to keep
## lines shorter than that.
description = \
"""
This script is a high-level summary for North Campus
including (but not limited to):
  - Overall Size of Bargaining Unit
  - Relative size of:
      - North Campus
      - Engineers
      - Stewarded NC GSI's
      - NC International Students
  - Membership by:
      - Overall
      - North Campus
      - Engineers
      - Stewarded NC Depts
      - Unstewarded NC Depts
      - NC Internationl Students
      - NC New Hires
      - NC Engin PhDs
      - NC Engin Masters


Notes:
  - Summary data is exported to: "results/nc_summary.csv"
  - Some information should be updated in the script
    when it is run on new data. The varibles are at the 
    top of the file.
      - The threshold date to be considered a "new hire"
      - The most recent stewards data. This data is 
        exported from: 
          Local Database ->  Groups -> Stewards' Council
"""
# Threshold date for "new hires"
NEW_HIRE_DATE = date(2017,05,01) # (year,month,day)

# File to dump summary data
OUT_FILE = os.getcwd()+'/results/'+'nc_summary.csv'

# Import list of stewards
stewards = kt.importstews(os.getcwd()+'/data/'+'stewards5-7-2019.csv')


def processing_function(raw):
    """
    This is the top-level function for processing data.
    
    The function is meant to be passed to the importer (in this case GuiIO).
    The importer will call this function after it has parsed the raw data.
    """

    # Sort stewarded & unstewarded depts
    STEWARDED_ENGIN_DEPTS = set(stewards.keys()) & kt.ENGINEERING_DEPTS
    UNSTEWARDED_ENGIN_DEPTS = kt.ENGINEERING_DEPTS - STEWARDED_ENGIN_DEPTS

    STEWARDED_NC_DEPTS = set(stewards.keys()) & kt.NORTH_CAMPUS_DEPTS
    UNSTEWARDED_NC_DEPTS = kt.NORTH_CAMPUS_DEPTS - STEWARDED_NC_DEPTS

    ##############################
    # Filter data in all the ways
    ##############################
    actives     = kt.filterdata(raw, kt.selectors.allactives)
    nc          = kt.filterdata(actives, kt.selectors.northcampus)
    engin       = kt.filterdata(actives, kt.selectors.engineers)

    # International Students
    nc_itnl     = kt.filterdata(nc, kt.selectors.itnl)
    nc_permres  = kt.filterdata(nc, kt.selectors.permres)

    # Stewarded / Unstewarded
    nc_stewarded= kt.filterdata(
                nc,
                lambda person: kt.selectors.bydept(person,STEWARDED_NC_DEPTS)
            )
    nc_unstewarded= kt.filterdata(
                nc,
                lambda person: kt.selectors.bydept(person,UNSTEWARDED_NC_DEPTS)
            )
    engin_stewarded= kt.filterdata(
            engin,
            lambda person: kt.selectors.bydept(person,STEWARDED_ENGIN_DEPTS)
            )
    engin_unstewarded= kt.filterdata(
            engin,
            lambda person: kt.selectors.bydept(person,UNSTEWARDED_ENGIN_DEPTS)
            )

    # Hire Date
    nc_newhires = kt.filterdata(
                nc, 
                lambda person: kt.selectors.hiredafter(person,NEW_HIRE_DATE)
            )

    nc_oldhires = kt.filterdata(
                nc, 
                lambda person: kt.selectors.hiredbefore(person,NEW_HIRE_DATE)
            )

    nc_nohiredate = kt.filterdata(nc, kt.selectors.nohiredate)

    # Degree Program
    engin_phd     = kt.filterdata(
                engin, 
                lambda person: kt.selectors.bydegree(person,['PhD'])
            )
    engin_masters = kt.filterdata(
                engin, 
                lambda person: kt.selectors.bydegree(person, kt.MASTERS)
            )

    ###############
    # Count things
    ###############

    # Unit sizes
    bargaining_unit_size    = len(actives)
    north_campus_size       = len(nc)
    engineering_size        = len(engin)
    overall_members         = kt.count_duespayers(actives)
    nc_members              = kt.count_duespayers(nc)
    engin_members           = kt.count_duespayers(engin)

    # Number of actives currently stewarded
    total_stewarded_nc     = len(nc_stewarded)
    total_unstewarded_nc   = len(nc_unstewarded)
    total_stewarded_engin  = len(engin_stewarded)
    total_unstewarded_engin= len(engin_unstewarded)
    nc_stewarded_members   = kt.count_duespayers(nc_stewarded)
    nc_unstewarded_members = kt.count_duespayers(nc_unstewarded)
    engin_stewarded_members= kt.count_duespayers(engin_stewarded)
    engin_unstewarded_members= kt.count_duespayers(engin_unstewarded)

    # International students
    total_intl      = len(nc_itnl)
    total_permres   = len(nc_permres)
    intl_members    = kt.count_duespayers(nc_itnl)
    permres_members = kt.count_duespayers(nc_permres)

    # New Hires
    total_newhires  = len(nc_newhires)
    total_oldhires  = len(nc_oldhires)
    total_nohiredate= len(nc_nohiredate)
    newhire_members = kt.count_duespayers(nc_newhires)
    oldhire_members = kt.count_duespayers(nc_oldhires)


    # Degree Program
    total_phd       = len(engin_phd)
    total_masters   = len(engin_masters)
    phd_members     = kt.count_duespayers(engin_phd)
    masters_members = kt.count_duespayers(engin_masters)
   

    ######################################
    # Derived Results
    ######################################
    labels = []
    results= []

    labels += ['Current Bargaining Unit Size']
    results+= [bargaining_unit_size]

    labels += ['Relative Size of North Campus (%)']
    results+= [(100.0*north_campus_size)/bargaining_unit_size]

    labels += ['Relative Number of Engineers on NC (%)']
    results+= [(100.0*engineering_size)/north_campus_size]

    labels += ['Relative Number of NC GSIs with >1 Steward (%)']
    results+= [(100.0*total_stewarded_nc)/north_campus_size]

    labels += ['Relative Number of NC International Students (%)']
    results+= [(100.0*total_intl)/north_campus_size]

    # labels += ['Relative Number of NC Permanent Resident Students (%)']
    # results+= [(100.0*total_permres)/north_campus_size]

    labels += ['']
    results+= ['']

    labels += ['Overall GEO Membership (%)']
    results+= [(100.0*overall_members)/bargaining_unit_size]

    labels += ['North Campus Membership (%)']
    results+= [(100.0*nc_members)/north_campus_size]

    labels += ['Engineering Membership (%)']
    results+= [(100.0*engin_members)/engineering_size]

    labels += ['Membership Among Stewarded NC Depts (%)']
    results+= [(100.0*nc_stewarded_members)/total_stewarded_nc]

    labels += ['Membership Among Unstewarded NC Depts (%)']
    results+= [(100.0*nc_unstewarded_members)/total_unstewarded_nc]

    labels += ['']
    results+= ['']

    labels += ['Relative # of International Students on NC (%)']
    results+= [(100.0*total_intl)/north_campus_size]

    labels += ['Membership Among International Students (%)']
    results+= [(100.0*intl_members)/total_intl]

    # labels += ['Membership Among Permanent Residents (%)']
    # results+= [(100.0*permres_members)/total_permres]

    labels += ['']
    results+= ['']

    labels += ['Relative # of New Hires on NC (%)']
    results+= [(100.0*total_newhires)/north_campus_size]

    labels += ['Membership Among New Hires (%)']
    results+= [(100.0*newhire_members)/total_newhires]

    labels += ['Membership Among Old Hires (%)']
    results+= [(100.0*oldhire_members)/total_oldhires]

    labels += ['Number of People w/o Known Hire Dates']
    results+= [total_nohiredate]

    labels += ['']
    results+= ['']

    labels += ['Relative # of Masters Students in Engineering (%)']
    results+= [(100.0*total_masters)/engineering_size]

    labels += ['Membership Among Engineering PhDs (%)']
    results+= [(100.0*phd_members)/total_phd]

    labels += ['Membership Among Engineering Masters (%)']
    results+= [(100.0*masters_members)/total_masters]

    labels += ['']
    results+= ['']



    # Display summary results
    print('\n')
    display_results(labels,results)

    print('Unstewarded Departments:')
    for d in UNSTEWARDED_NC_DEPTS: print(d)

    print('\n')



    # Print summary results to csv
    kt.writecsv_summary(zip(labels,results), OUT_FILE)



    # dump all local variables to file
    # v = locals()



    return None



def display_results(labels, results):
    TAB_STOP = 70
    for l,r in zip(labels,results):
        if l=='': print(''); continue

        tab = int(TAB_STOP-len(l))
        if tab<0: tab = 0

        print(l+':'+' '*tab+str(r))


