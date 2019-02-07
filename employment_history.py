# -*- coding: utf-8 -*-

import knack_tools as kt


import os
from copy import deepcopy
from datetime import date

# Relative paths are tricky sometimes; better to use full paths
INPATH  = os.getcwd()+'/data/'
OUTPATH = os.getcwd()+'/results/'


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

# Import knack data
raw     = kt.importcsv(INPATH+'all_actives-3-19-18.csv')
actives = kt.filterdata(raw, kt.selectors.allactives)


termcount_total = {}
termcount_members = {}
for umid in actives:
    person = actives[umid]

    # Process 'Employment Period' Field
    termcount = len(person['Employment Period'].split(', '))
    person['Term Count'] = termcount
    
    # Count Total # for each term count
    try:
        termcount_total[termcount] = termcount_total[termcount] + 1
    except KeyError:
        termcount_total[termcount] = 1
    
    # Count # of members for each term count
    if person['Member Status'] == 'Union Dues':
        try:
            termcount_members[termcount] = termcount_members[termcount] + 1
        except KeyError:
            termcount_members[termcount] = 1
    else:
        if not termcount in termcount_members:
            termcount_members[termcount] = 0


# Summarize
membership = {}
for termcount in termcount_total.keys():
    membership[termcount] = termcount_members[termcount] / \
                                float(termcount_total[termcount])

    print(str(termcount) + ' Terms Taught:')
    print(str_2col('Total Count:',str(termcount_total[termcount]),30))
    print(str_2col('Membership:', str(membership[termcount]*100)+' %',30))
    print('\n')





# # Import historical member list
# member_lists = parsemembers(INPATH+'historical members list.csv')

# # Import 

# hr_data = dict( zip(FILENAMES.keys(),[None]*len(FILENAMES)) )
# newhire_data = deepcopy(hr_data)
# memberships  = deepcopy(hr_data)
# nh_percent   = deepcopy(hr_data)
# nh_memberships= deepcopy(hr_data)
# for term in TERMS:
#     # Import appropriate HR data
#     hr_data[term], _, _ = parsebyid(kt._readcsv(INPATH+FILENAMES[term]))

#     # Pick out new hires from hr data
#     temp = kt.filterdata(
#                 hr_data[term], 
#                 lambda person: hiredafter( person,
#                                         NEW_HIRE_DATES[term][0] )
#             )
#     print(NEW_HIRE_DATES[term][0])
#     newhire_data[term] = kt.filterdata(
#                 temp, 
#                 lambda person: hiredbefore( person,
#                                         NEW_HIRE_DATES[term][1] )
#             )
#     print(term)
#     # Track overall membership over time
#     memberships[term] = float(len(member_lists[term])) \
#                         / UNIT_SIZES[term]

#     # Track turnover over time
#     nh_percent[term] =  float(len(newhire_data[term])) \
#                           / UNIT_SIZES[term]

#     # Track membership among new-hires over time
#     nh_members = set(member_lists[term]) & set(newhire_data[term].keys())
#     nh_memberships[term] =  float(len(nh_members)) \
#                           / float(len(newhire_data[term]))


# # Print results
# print('Overall Membership:')
# for term in TERMS:
#     print(str_2col('Membership '+term+':',str(memberships[term]*100)+' %',30))

# print('\n')
# print('Unit Turnover:')
# for term in TERMS:
#     print(str_2col(term+':',str(nh_percent[term]*100)+' %',30))

# print('\n')
# print('New Hire Membership:')
# for term in TERMS:
#     print(str_2col('Membership '+term+':',str(
#                                 nh_memberships[term]*100)+' %',30)
#                             )

# # Export results to csv file
# results = [['Term', 'Overall Membership (%)',
#                     'Turnover (%)',
#                     'New Hire Membership (%)']]
# for term in TERMS:
#     results.append([term, str(memberships[term]*100), 
#                           str(nh_percent[term]*100),
#                           str(nh_memberships[term]*100)])
# kt.writecsv_summary(results, OUTPATH+'employment_history_summary.csv')