# -*- coding: utf-8 -*-
"""
Mcommunity Scraper Tool
v0.1

Note: If you don't have the "config.py" file in this folder,
      you need to get it from a staff member (or someone on 
      the tech committee). This is for security.
"""

try:
    import config
except (ImportError):
    raise Exception('Can\'t find access tokens for Mcommunity. \n'+
                'You must request tokens from the tech committee '+
                'to run the scraper tool.')
import requests
import urllib
import base64

## TO DO: It'd be nice to reference the main 'constants.py' file for this
##          rather than duplicating it...
MASTERS = {"MHSA","MLArch", "DNP" , "MUP", "MHI", "MSW", "MFA", "AMusD", "MBA",
           "MPH", "MAcc", "MPP", "MArch", "MSE", "MEng", "MSI", "MS", "MA"}


###############################################################################
# Mcommunity Scraper Tool
###############################################################################


class Scraper(object):
    """Connects to m-community and looks up information"""
    url = "https://apigw.it.umich.edu/um/MCommunity/People/minisearch/"

    ## I've had to switch the token url at least twice and I'm not sure why.
    ## If you're having trouble getting tokens, try switching this.
    # token_url = ("https://apigw.it.umich.edu/um/bf/oauth2/token"
    #              "?grant_type=client_credentials&scope=mcommunity")
    token_url = ("https://apigw.it.umich.edu/um/inst/oauth2/token"
                 "?grant_type=client_credentials&scope=mcommunity")

    client_id = config.client_id
    client_secret = config.client_secret
    token_access_string = base64.b64encode(client_id + ":" + client_secret)

    token_access_header = {'Authorization': 'Basic ' + token_access_string}
    
    def __init__(self):
        pass

    ###########################################
    # M-Community API methods
    ###########################################

    def _apicall(self,access_token, client_id, query):
        """Makes basic apicalls to the mcommunity"""
        header = {'Authorization': 'Bearer ' + access_token,
                  'X-IBM-Client-Id': client_id}

        # Need to sanitize the query b/c it gets put
        # straight into a url
        clean_query = urllib.quote(query.encode('utf8'))
        r = requests.get(self.url+clean_query, headers=header)
        try: return r.json()
        except: return False


    def querydb(self,query):
        token_call = requests.post(self.token_url,
                            headers=self.token_access_header).json()
        try:
            access_token = str(token_call['access_token'])
        except KeyError:
            print(token_call)
            raise Exception('Error getting Mcommunity tokens. Try '+
                            'switching the token_url.')
        return self._apicall(access_token, self.client_id, query)


    ###########################################
    # Response Processing methods
    ###########################################

    def choose_person(self, query_result, knack_result):
        """
        Given the json from an mcommunity api call, compare as many pieces 
        of information we have and choose the one that has the highest 
        match %. Return chosen person.
        """
        # Returns list of all elements in 'l' that contain the string 's'
        findstr_inlist = lambda s,l: [ ii for ii in l if s in ii ]

        people = query_result['person']
        scores = []
        for p in people:
            knack_count = 0
            query_count = 0
            # Check Employment Status
            try:
                if knack_result['Employment Status']=='Active':
                    knack_count += 1
                    matches = findstr_inlist(
                                'Graduate Student Instructor', p['title']
                                )
                    if matches:
                        query_count += 1
            except KeyError:
                pass

            # Check for Department Name in various places
            # TO DO: make dictionary linking knack depts to mcommunity depts
            try:
                if knack_result['Department']:
                    knack_count += 1
                    matches = findstr_inlist(
                                knack_result['Department'], p['title']
                                )
                    matches = matches+findstr_inlist(
                                knack_result['Department'], p['affiliations']
                                )
                    if matches:
                        query_count += 1
            except KeyError:
                pass

            # Check against known uniqname
            try:
                if knack_result['Employer Unique Name']:
                    knack_count += 1
                    if p['uniqname'] == knack_result['Employer Unique Name']:
                        query_count += 1
            except KeyError:
                pass


            if not knack_count: 
                break
            scores = scores+[query_count/float(knack_count)]

        # If we don't know anything about this person, make a naive choice
        if (not scores):
            if len(people)==1:
                return (people[0], -1)
            else: return (False, -1)

        # Check for multiple matches
        idx = [ii for ii,s in enumerate(scores) if s==max(scores)]
        if len(idx) > 1: 
            # for p in people:
            #     print(p)
            #     print('\n')
            return (False, scores[idx[0]])

        # Otherwise, let's choose the best score:
        idx = idx[0]
        return (people[idx], scores[idx])


    def getenrolled(self, person):
        try:affiliations = person[u'affiliation']
        except:return ["", ""]
        stud = filter(lambda x: "Student" in x, affiliations)
        for x in stud:
            if "PhD" in x:
                return [x[:-14], "PhD"]
        for x in stud:
            for m in MASTERS:
                if m in x:
                    return [x[:-10-len(m)], m]
        for x in stud:
            if "Law" in x:
                return ["Law", "JD"]
        for x in stud:
            if "Doc" in x:
                return ["School of Information", "PhD"]
        return ["Unknown", "Unknown"]




