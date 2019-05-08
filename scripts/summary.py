# -*- coding: utf-8 -*-

import knack_tools as kt
from datetime import date, datetime
import os


name = "Overall Summary"

## Default textbox width is 60 characters.
## To keep text from wrapping, it's best to keep
## lines shorter than that.
description = \
"""
This script is a high-level summary for the bargaining unit
including (but not limited to):
  - Overall Size of Bargaining Unit
  - Relative size of:
      - Stewarded GSI's
      - International Students
  - Membership by:
      - Overall
      - Stewarded Depts
      - Unstewarded Depts
      - Internationl Students
      - New Hires
      - PhDs
      - Masters


Notes:
  - Summary data is exported to: "results/summary.csv"
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
OUT_FILE = os.getcwd()+'/results/'+'summary.csv'

# Import list of stewards
stewards = kt.importstews(os.getcwd()+'/data/'+'stewards5-7-2019.csv')


def processing_function(raw):
    """
    This is the top-level function for processing data.
    
    The function is meant to be passed to the importer (in this case GuiIO).
    The importer will call this function after it has parsed the raw data.
    """

    # Sort stewarded & unstewarded depts
    STEWARDED_DEPTS = set(stewards.keys()) & kt.ALL_DEPTS
    UNSTEWARDED_DEPTS = kt.ALL_DEPTS - STEWARDED_DEPTS

    ##############################
    # Filter data in all the ways
    ##############################
    actives     = kt.filterdata(raw, kt.selectors.allactives)
    nc          = kt.filterdata(actives, kt.selectors.northcampus)

    # International Students
    itnl     = kt.filterdata(actives, kt.selectors.itnl)
    permres  = kt.filterdata(actives, kt.selectors.permres)

    # Stewarded / Unstewarded
    stewarded= kt.filterdata(
                actives,
                lambda person: kt.selectors.bydept(person,STEWARDED_DEPTS)
            )
    unstewarded= kt.filterdata(
                actives,
                lambda person: kt.selectors.bydept(person,UNSTEWARDED_DEPTS)
            )

    # Hire Date
    newhires = kt.filterdata(
                actives, 
                lambda person: kt.selectors.hiredafter(person,NEW_HIRE_DATE)
            )

    oldhires = kt.filterdata(
                actives, 
                lambda person: kt.selectors.hiredbefore(person,NEW_HIRE_DATE)
            )

    nohiredate = kt.filterdata(actives, kt.selectors.nohiredate)

    # Degree Program
    phd     = kt.filterdata(
                actives, 
                lambda person: kt.selectors.bydegree(person,['PhD'])
            )
    masters = kt.filterdata(
                actives, 
                lambda person: kt.selectors.bydegree(person, kt.MASTERS)
            )

    ###############
    # Count things
    ###############

    # Unit sizes
    bargaining_unit_size    = len(actives)
    overall_members         = kt.count_duespayers(actives)

    # Number of actives currently stewarded
    total_stewarded     = len(stewarded)
    total_unstewarded   = len(unstewarded)
    stewarded_members   = kt.count_duespayers(stewarded)
    unstewarded_members = kt.count_duespayers(unstewarded)

    # International students
    total_intl      = len(itnl)
    total_permres   = len(permres)
    intl_members    = kt.count_duespayers(itnl)
    permres_members = kt.count_duespayers(permres)

    # New Hires
    total_newhires  = len(newhires)
    total_oldhires  = len(oldhires)
    total_nohiredate= len(nohiredate)
    newhire_members = kt.count_duespayers(newhires)
    oldhire_members = kt.count_duespayers(oldhires)


    # Degree Program
    total_phd       = len(phd)
    total_masters   = len(masters)
    phd_members     = kt.count_duespayers(phd)
    masters_members = kt.count_duespayers(masters)
   

    ######################################
    # Derived Results
    ######################################
    labels = []
    results= []

    labels += ['Current Bargaining Unit Size']
    results+= [bargaining_unit_size]

    labels += ['Relative Number of GSIs with >1 Steward (%)']
    results+= [(100.0*total_stewarded)/bargaining_unit_size]

    labels += ['Relative Number of International Students (%)']
    results+= [(100.0*total_intl)/bargaining_unit_size]

    # labels += ['Relative Number of NC Permanent Resident Students (%)']
    # results+= [(100.0*total_permres)/bargaining_unit_size]

    labels += ['']
    results+= ['']

    labels += ['Overall GEO Membership (%)']
    results+= [(100.0*overall_members)/bargaining_unit_size]

    labels += ['Membership Among Stewarded Depts (%)']
    results+= [(100.0*stewarded_members)/total_stewarded]

    labels += ['Membership Among Unstewarded Depts (%)']
    results+= [(100.0*unstewarded_members)/total_unstewarded]

    labels += ['']
    results+= ['']

    labels += ['Relative # of International Students (%)']
    results+= [(100.0*total_intl)/bargaining_unit_size]

    labels += ['Membership Among International Students (%)']
    results+= [(100.0*intl_members)/total_intl]

    # labels += ['Membership Among Permanent Residents (%)']
    # results+= [(100.0*permres_members)/total_permres]

    labels += ['']
    results+= ['']

    labels += ['Relative # of New Hires (%)']
    results+= [(100.0*total_newhires)/bargaining_unit_size]

    labels += ['Membership Among New Hires (%)']
    results+= [(100.0*newhire_members)/total_newhires]

    labels += ['Membership Among Old Hires (%)']
    results+= [(100.0*oldhire_members)/total_oldhires]

    labels += ['Number of People w/o Known Hire Dates']
    results+= [total_nohiredate]

    labels += ['']
    results+= ['']

    labels += ['Relative # of Masters Students (%)']
    results+= [(100.0*total_masters)/bargaining_unit_size]

    labels += ['Membership Among Masters Students (%)']
    results+= [(100.0*masters_members)/total_masters]

    labels += ['Membership Among PhD Students (%)']
    results+= [(100.0*phd_members)/total_phd]

    labels += ['']
    results+= ['']



    # Display summary results
    print('\n')
    display_results(labels,results)

    print('Unstewarded Departments:')
    for d in UNSTEWARDED_DEPTS: print(d)

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


