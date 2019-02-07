"""
selectors.py
v0.1

Selector functions meant to be used for filtering knack data.
"""
from datetime import date
from constants import *


def bydept(person, dept_list):
    """
    If person is in one of the listed depts, pass the data.
    Otherwise return None.
    """
    for d in dept_list:
        if person['Department'] == d:
            return person
    return None

def bydegree(person, degree_list):
    """
    If person is in one of the listed degrees, pass the data.
    Otherwise return None.
    """
    for d in degree_list:
        if person['Degree'] == d:
            return person
    return None

def allactives(person):
    """
    If person is currently in the bargaining unit, pass the data.
    Otherwise return None.
    """
    if person['Employment Status'] == 'Active':
        return person
    return None

def itnl(person):
    """
    If person is an international student, pass the data.
    Otherwise return None.
    """
    if person['Citizenship'] == 'International Student':
        return person
    return None

def permres(person):
    """
    If person is a permanent resident, pass the data.
    Otherwise return None.
    """
    if person['Citizenship'] == 'Permanent Resident':
        return person
    return None

def citizen(person):
    """
    If person is a citizen, pass the data.
    Otherwise return None.
    """
    if person['Citizenship'] == 'Citizen':
        return person
    return None

def hiredafter(person,hiredate):
    """
    If person was hired after 'hiredate', pass the data.
    Otherwise return None.
    """
    pdate_str = person['Hire Date']
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
    pdate_str = person['Hire Date']
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

def nohiredate(person):
    """
    If person doesn't have a hire date, pass the data.
    Otherwise return None.
    """
    pdate_str = person['Hire Date']
    if not pdate_str:
        return person

    try:
        m,d,y = pdate_str.split('/')
        pdate = date(int(y),int(m),int(d))
    except:
        print('At '+person['Individual']+':')
        print('Error parsing date ('+pdate_str+')')
        return person

    return None

def nonpayers(person):
    if person['Member Status'] == 'Non-Payer': return person
    return None

def duespayers(person):
    if person['Member Status'] == 'Union Dues': return person
    return None


def column_is_empty(person,column):
    if person[column]: return person
    return None


def northcampus(person):
    return bydept(person, NORTH_CAMPUS_DEPTS)

def engineers(person):
    return bydept(person, ENGINEERING_DEPTS)


