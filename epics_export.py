#!/usr/bin/env python

import os
import json
import argparse
import requests
from dateutil.parser import parse as dateparse
from dotenv import load_dotenv


def printCount(filter, count) :
	if filter == "In Progress":
		print("Architecture in Progress: %d" % count)
	elif filter == "Ready for Eng Review":
		print("Ready for engineering review: %d" % count)
	elif filter == "DA Review Required":
		print("DA review required: %d" % count)
	elif filter == "Done":
		print("Done: %d" % count)
	elif filter == "":
		print("Not reviewed: %d" % count)
	elif filter == "Required":
		print("Architecture Required: %d" % count)
	elif filter == "Not Required":
		print("Architecture not required: %d" % count)
	elif filter == "Re-review":
		print("Re-review: %d" % count)
	elif filter == "All":
		print("All Stories: %d" % count)
	else:
		print("Number of stories = %d" % count)

def query(scope, filter, debug=False):
    if filter == "All":
        q = """
{
  "from": "Epic",
  "select": [
    "ID.Name",
    "Name",
    "Category.Name",
    "Number",
    "Custom_TSAStatus2.Name",
    "Custom_TSADate",
    "Custom_ArchAcceptReject"
  ],
  "sort": [
    "+Order"
  ],
  "where": {
    "Scope.Name": "%s",
    "Category.Name": "Big Story"
  }
}
""" % (scope)

    else:
        q = """
{
  "from": "Epic",
  "select": [
    "ID.Name",
    "Name",
    "Category.Name",
    "Number",
    "Custom_TSAStatus2.Name",
    "Custom_TSADate",
    "Custom_ArchAcceptReject"
  ],
  "sort": [
    "+Order"
  ],
  "where": {
    "Scope.Name": "%s",
    "Custom_TSAStatus2.Name": "%s",
    "Category.Name": "Big Story"
  }
}
""" % (scope, filter)

    oid_accept = 'Custom_Arch_Accept_Reject:118164'
    oid_reject = 'Custom_Arch_Accept_Reject:118165'
    url = args.endpoint + '/query.v1'
    req = requests.post(url, data=q, headers=headers)
    stories = req.json()[0]
    #print (stories)
    i = 0
    printCount(filter, len(stories))
    for i in range(len(stories)):
        s = stories[i]
        if debug:
            print(s)
        if filter == "Required":
            ds = s['Custom_TSADate']
            if ds:
                ds = dateparse(ds)
                ds = ds.strftime('%m/%d/%Y')
            else:
                ds = "TBD"
            print("%s [%s] - Target %s" % (s['Name'], s['Number'], ds))
        elif filter == "All":
            accept_reject = s['Custom_ArchAcceptReject']
            if accept_reject :
                if accept_reject['_oid'] == oid_reject :
                    print("%s [%s] %s Rejected" % (s['Name'], s['Number'], s['Custom_TSAStatus2.Name']))
                else:
                    print("%s [%s] %s" % (s['Name'], s['Number'], s['Custom_TSAStatus2.Name']))
            else :
                print("%s [%s] %s" % (s['Name'], s['Number'], s['Custom_TSAStatus2.Name']))
        else:
            accept_reject = s['Custom_ArchAcceptReject']
            if accept_reject :
                if accept_reject['_oid'] == oid_reject :
                    print("%s [%s] Rejected" % (s['Name'], s['Number']))
                else:
                    print("%s [%s]" % (s['Name'], s['Number']))
            else :
                print("%s [%s]" % (s['Name'], s['Number']))

if __name__ == '__main__':
    dotenv_path="/Users/acasella/.versionone/env"
    load_dotenv(dotenv_path)
    parser = argparse.ArgumentParser(description='export versionone stories.')
    parser.add_argument('--token', default=os.environ.get('VERSION_ONE_TOKEN'))
    parser.add_argument('--endpoint', default=os.environ.get('VERSION_ONE_ENDPOINT'))
    parser.add_argument("--scope", default="Athena 3.X")
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("tsa_status", default="")
    args = parser.parse_args()
    headers = {}

    if args.token:
        headers['Content-Type'] = 'application/json'
        headers['Authorization'] = 'Bearer ' + args.token

    query(args.scope, args.tsa_status, args.debug)
