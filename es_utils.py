#!/bin/python
import sys,urllib2 , json
from datetime import datetime
#Function to store data in elasticsearch using urllib2
def send_payload(index,document,id,payload):
  try:
    passw=open('/data/secrets/github_hook_secret_cmsbot','r').read().strip()
  except Exception as e:
    print "Couldn't read the secrets file" , str(e)
  #form the url with index name , doc name , and uniq id
  url="http://%s/%s/%s/%s" % ('cmses-master01.cern.ch:9200',index,document,id)
  #send the data to elasticsearch
  passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
  passman.add_password(None,url, 'user_name', passw)
  auth_handler = urllib2.HTTPBasicAuthHandler(passman)
  opener = urllib2.build_opener(auth_handler)
  try:
    urllib2.install_opener(opener)
    content = urllib2.urlopen(url,payload)
  except Exception as e:
    print "Couldn't send data to elastic search" , str(e)
