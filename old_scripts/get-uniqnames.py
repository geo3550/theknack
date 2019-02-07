#!/bin/python2

from Tkinter import *
import tkFileDialog
import requests
import json
# import unicodecsv as csv
import csv
import os, time
import base64

url = "https://apigw.it.umich.edu/um/MCommunity/People/minisearch/"
token_url = ("https://apigw.it.umich.edu/um/inst/oauth2/token"
             "?grant_type=client_credentials&scope=mcommunity")

client_id = "fe82ec34-5776-4b58-9ba8-0939ce88a5f9"
client_secret = "eC8oI8lJ0aH3bL3wX3kY7wT0iH7nT2pR5mH5cT4yS1jU6bP8cJ"
token_access_string = base64.b64encode(client_id + ":" + client_secret)

token_access_header = {'Authorization': 'Basic ' + token_access_string}

masters = ("MHSA","MLArch", "DNP" , "MUP", "MHI", "MSW", "MFA", "AMusD", "MBA",
           "MPH", "MAcc", "MPP", "MArch", "MSE", "MEng", "MSI", "MS", "MA")

def apicall(access_token, client_id, query):
    """Makes basic apicalls to the mcommunity"""
    header = {'Authorization': 'Bearer ' + access_token,
              'X-IBM-Client-Id': client_id}
    try:
        r = requests.get(url+query, headers=header)
    except:
        print(url+query)
        print(header)
        raise()
    try: return r.json()
    except: return False

def getun(request):
    """Given the json from an mcommunity api call, returns the uniqname,
    or else False"""
    p = request.values()[0]
    if len(p)==1:
        try: return [p[0][u'uniqname']]
        except: return False
    else: return False

def getenrolled(request):
    try:affiliations = request[u'person'][0][u'affiliation']
    except:return False
    stud = filter(lambda x: "Student" in x, affiliations)
    for x in stud:
        if "PhD" in x:
            return [x[:-14], "PhD"]
    for x in stud:
        for m in masters:
            if m in x:
                return [x[:-10-len(m)], m]
    for x in stud:
        if "Law" in x:
            return ["Law", "JD"]
    for x in stud:
        if "Doc" in x:
            return ["School of Information", "PhD"]
    return ["Unknown", "Unknown"]

def processfile(filename):
    """given a file with firstnames and last names and an access token,
    create a new file with uniqnames and enrolled departments appended"""
    dirname = os.path.dirname(filename)
    os.chdir(dirname)

    lines = []
    found = []
    remaining = []
    numremaining = 0
    failures = 0

    with open(filename, "rb") as f:
        csvreader = csv.reader(f)
        lines = [line for line in csvreader]
    header = lines[0]+["Uniqname", "Email", "Enrolled Department", "Degree"]
    i1 = lines[0].index("FirstName")
    i2 = lines[0].index("LastName")
    remaining = lines[1:]
    numremaining = len(remaining)

    # get uniqnames
    print "Getting uniqnames ..."
    while numremaining != 0 and failures < 3:
        token_call = requests.post(token_url, headers=token_access_header).json()
        access_token = str(token_call['access_token'])
        # for some reason, we need to try to get the uniqnames multiple times,
        # so we loop until we fail to get new entries 3 times in a row
        print "\tnumremaining: %d\tfailures: %d" % (numremaining, failures)
        for line in remaining:
            query = line[i1]+" "+line[i2]
            print(query)
            result = apicall(access_token, client_id, query)
            # print(len(result['person']))
            # print(len(remaining))
            # print(query)
            # print(result['person'][1]['email'])
            # try:
            #     print(result['person'][1]['affiliation'])
            # except:
            #     print('Error')
            #     print('\n')
            if result:
                newdata = getun(result)
                if newdata:
                    newdata.append(newdata[0]+"@umich.edu")
                    found.append(line+newdata)
                    remaining.remove(line)
                    failures = 0
            time.sleep(.005)
        if numremaining == len(remaining):
            failures += 1
        else:
            numremaining = len(remaining)
        time.sleep(.01)

    # get enrolled department of people whose uniqnames were found
    i3 = header.index("Uniqname")
    enrolledfound = []
    enrolledremaining = found
    numremaining = len(enrolledremaining)
    failures = 0
    print "Getting enrolled departments ..."
    while numremaining != 0 and failures < 3:
        token_call = requests.post(token_url, headers=token_access_header).json()
        access_token = str(token_call['access_token'])
        # for some reason, we need to do this multiple times as well
        print "\tnumremaining: %d\tfailures: %d" % (numremaining, failures)
        for line in enrolledremaining:
            query = line[i3]
            result = apicall(access_token, client_id, query)
            if result:
                newdata = getenrolled(result)
                if newdata:
                    enrolledfound.append(line+newdata)
                    enrolledremaining.remove(line)
                    failures = 0
            time.sleep(.005)
        if numremaining == len(enrolledremaining):
            failures += 1
        else:
            numremaining = len(enrolledremaining)
        time.sleep(.01)

    # write data
    print "Writing data ..."
    with open("out.csv", "wb") as f:
        csvwriter = csv.writer(f)
        csvwriter.writerow(header)
        for line in enrolledfound:
            csvwriter.writerow(line)
        for line in enrolledremaining:
            csvwriter.writerow(line)
        for line in remaining: 
            csvwriter.writerow(line)

    print "Done processing file!"

class Application(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.status = StringVar()
        self.filename = StringVar()
        self.createWidgets()
        self.grid()
    def createWidgets(self):
        #self.tokenprompt = Label(text = "Access token:")
        #self.tokenentry = Entry()
        self.filebutton = Button(self, text="Select input file", command=self.getfilename)
        self.filenameprompt = Label(textvariable = self.filename)
        self.getunbutton = Button(self, text="Get uniqnames!", command=self.getuns)
        self.statusprompt = Label(textvariable = self.status)

        #self.tokenprompt.grid(row=0, column=0)
        #self.tokenentry.grid(row=0, column=1)
        self.filenameprompt.grid(row=1, column=0, columnspan=2)
        self.filebutton.grid(row=2, column=0)
        self.getunbutton.grid(row=3, column=0)
        self.statusprompt.grid(row=3, column=1)
    def getfilename(self):
        self.filename.set(tkFileDialog.askopenfilename())
    def getuns(self):
        self.status.set("Processing ...")
        processfile(self.filename.get())
        self.status.set("Done!")
        
app = Application()
app.master.title("GEO Scrape-o-matic")
app.mainloop()
