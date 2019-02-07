# -*- coding: utf-8 -*-

import knack_tools as kt


import os
from copy import deepcopy
from datetime import date

# Relative paths are tricky sometimes; better to use full paths
INPATH  = os.getcwd()+'/data/historical data/'
OUTPATH = os.getcwd()+'/results/'

# I don't want to import multiple files just to count the total unit size,
# so I'm just doing it by hand. (from 'Member Payments By Semester.xlsx',
# just add the # of dues payers + # of fee payers)
UNIT_SIZES = {  
                'Summer 2014':  83 + 28,
                'Fall 2014':    1431-1 + 484,
                'Winter 2015':  1282 + 390,
                'Spring 2015':  121-1 + 37,
                'Summer 2015':  69-1 + 18,
                'Fall 2015':    1410-1 + 485-1,
                'Winter 2016':  1309-1 + 471-1,
                'Spring 2016':  123 + 33,
                'Summer 2016':  94 + 11,
                'Fall 2016':    1520 + 779,
                'Winter 2017':  1379 + 324,
                'Fall 2017':    2066,
                'Winter 2018':  1861
}

# Note: there doesn't seem to be a file for spring 2015 (should be may)?
#       using the summer file for now.
#
# ***REMBMER TO UPDATE MOST RECENT TERM AFTER IT IS OVER***
FILENAMES = {  
                'Summer 2014':  '2014 june.csv',
                'Fall 2014':    '2014 november.csv',
                'Winter 2015':  '2015 april.csv',
                'Spring 2015':  '2015 august.csv',
                'Summer 2015':  '2015 august.csv',
                'Fall 2015':    '2015 december.csv',
                'Winter 2016':  '2016 april.csv',
                'Spring 2016':  '2016 may.csv',
                'Summer 2016':  '2016 august.csv',
                'Fall 2016':    '2016 december.csv',
                'Winter 2017':  '2017 april.csv',
                'Fall 2017':    '2017 december.csv',
                'Winter 2018':  '2018 march.csv'
}

# Creates a window in which to look for hire dates: (beginning, end)
# Note: Dates are (year, month, day)
NEW_HIRE_DATES = {  
                'Summer 2014':  (date(2014,5,1), date(2014,8,1)),
                'Fall 2014':    (date(2014,8,1), date(2015,1,1)),
                'Winter 2015':  (date(2015,1,1), date(2015,5,1)),
                'Spring 2015':  (date(2015,5,1), date(2015,7,1)),
                'Summer 2015':  (date(2015,7,1), date(2015,8,1)),
                'Fall 2015':    (date(2015,8,1), date(2016,1,1)),
                'Winter 2016':  (date(2016,1,1), date(2016,5,1)),
                'Spring 2016':  (date(2016,5,1), date(2016,7,1)),
                'Summer 2016':  (date(2016,7,1), date(2016,8,1)),
                'Fall 2016':    (date(2016,8,1), date(2017,1,1)),
                'Winter 2017':  (date(2017,1,1), date(2017,5,1)),
                'Fall 2017':    (date(2017,8,1), date(2018,1,1)),
                'Winter 2018':  (date(2018,1,1), date(2018,5,1))
}


TERMS = (
                'Summer 2014',
                'Fall 2014',
                'Winter 2015',
                'Spring 2015',
                'Summer 2015',
                'Fall 2015',
                'Winter 2016',
                'Spring 2016',
                'Summer 2016',
                'Fall 2016',
                'Winter 2017',
                'Fall 2017',
                'Winter 2018'
)

###############################################################################
# Function Definitions
###############################################################################
def parsemembers(filename):
    lines = kt._readcsv(filename)

    # Sanitize column labels and find the Depatment column
    header = [elt.strip() for elt in lines[0]]

    # Create a dictionary with column labels as keys. Each entry is a list
    # of all umids in the given column
    members = dict(zip(header, [[]]*len(header)))
    for line in lines[2:-1]:
        for ii, r in enumerate(header):
            if line[ii]:
                members[r] = members[r] + [line[ii]]
            
    return members
    
def parsebyid(lines):
    """
    Given raw data, parse each line into a dictionary representing
    that person's data, then return a dictionary of each person,
    using UMIDs as the keys.
    """

    # Sanitize column labels and find the UMID column
    header = [elt.strip() for elt in lines[0]]
    id_index = header.index('Emplid')

    # Create dictionary for each person
    keys = header
    del keys[id_index]
    ids = []
    data = []
    for line in lines[1:]:
        thisid = line[id_index].strip()
        ids = ids+[ thisid ]
        del line[id_index]

        datum = dict(zip(keys,line))
        data = data+[ datum ]

    # Create overall dictionary of all the people
    return [dict(zip(ids,data)), header, ids]

def str_2col(text1,text2,tabwidth):
    TAB = tabwidth-len(text1)
    if TAB<1: TAB = 1
    return text1 + ' '*TAB + text2


def hiredafter(person,hiredate):
    """
    If person was hired after 'hiredate', pass the data.
    Otherwise return None.
    """
    pdate_str = person['Hire Begin Date']
    if not pdate_str:
        return None

    try:
        m,d,y = pdate_str.split('/')
        pdate = date(int(y),int(m),int(d))
    except:
        print('At '+person['Individual']+':')
        print('Error parsing date ('+pdate_str+')')
        return None

    if pdate >= hiredate:
        return person
    return None

def hiredbefore(person,hiredate):
    """
    If person was hired after 'hiredate', pass the data.
    Otherwise return None.
    """
    pdate_str = person['Hire Begin Date']
    if not pdate_str:
        return None

    try:
        m,d,y = pdate_str.split('/')
        pdate = date(int(y),int(m),int(d))
    except:
        print('At '+person['Individual']+':')
        print('Error parsing date ('+pdate_str+')')
        raise 
        return None

    if pdate < hiredate:
        return person
    return None


###############################################################################
# Main script
###############################################################################

# Import historical member list
member_lists = parsemembers(INPATH+'historical members list.csv')

# Import 

hr_data = dict( zip(FILENAMES.keys(),[None]*len(FILENAMES)) )
newhire_data = deepcopy(hr_data)
memberships  = deepcopy(hr_data)
nh_percent   = deepcopy(hr_data)
nh_memberships= deepcopy(hr_data)
for term in TERMS:
    # Import appropriate HR data
    hr_data[term], _, _ = parsebyid(kt._readcsv(INPATH+FILENAMES[term]))

    # Pick out new hires from hr data
    temp = kt.filterdata(
                hr_data[term], 
                lambda person: hiredafter( person,
                                        NEW_HIRE_DATES[term][0] )
            )
    print(NEW_HIRE_DATES[term][0])
    newhire_data[term] = kt.filterdata(
                temp, 
                lambda person: hiredbefore( person,
                                        NEW_HIRE_DATES[term][1] )
            )
    print(term)
    # Track overall membership over time
    memberships[term] = float(len(member_lists[term])) \
                        / UNIT_SIZES[term]

    # Track turnover over time
    nh_percent[term] =  float(len(newhire_data[term])) \
                          / UNIT_SIZES[term]

    # Track membership among new-hires over time
    nh_members = set(member_lists[term]) & set(newhire_data[term].keys())
    nh_memberships[term] =  float(len(nh_members)) \
                          / float(len(newhire_data[term]))


# Print results
print('Overall Membership:')
for term in TERMS:
    print(str_2col('Membership '+term+':',str(memberships[term]*100)+' %',30))

print('\n')
print('Unit Turnover:')
for term in TERMS:
    print(str_2col(term+':',str(nh_percent[term]*100)+' %',30))

print('\n')
print('New Hire Membership:')
for term in TERMS:
    print(str_2col('Membership '+term+':',str(
                                nh_memberships[term]*100)+' %',30)
                            )

# Export results to csv file
results = [['Term', 'Overall Membership (%)',
                    'Turnover (%)',
                    'New Hire Membership (%)']]
for term in TERMS:
    results.append([term, str(memberships[term]*100), 
                          str(nh_percent[term]*100),
                          str(nh_memberships[term]*100)])
kt.writecsv_summary(results, OUTPATH+'historical_membership.csv')