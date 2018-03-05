import json
import os, errno
import urllib
import urllib.error
import urllib.request
from ckanapi import RemoteCKAN
scidmurl="https://scidm.nchc.org.tw"
aidmurl="https://aidm.nchc.org.tw"
ua = 'ckanapiexample/1.0 (+http://example.com/my/website)'
key = ""
url = aidmurl
aiDatasets = {}
dataRootDir = "datasets"

dm = RemoteCKAN(url, user_agent=ua, apikey=key)
#pkgs = dm.action.package_list()
# for scidm
#pkgs = dm.action.organization_show(id="nchc-aidm",include_datasets=True)
# for aidm
#pkgs = dm.action.group_show(id="ai",include_datasets=True)
#print(pkgs)

def retrievePackages():
    pkgs = dm.action.group_show(id="ai",include_datasets=True)
    #for key,value in pkgs.items():
    #    print(key,": ",value)

    aipkgs = pkgs['packages']

    for aipkg in aipkgs:
        #print("==== package ====")
        #for key,value in aipkg.items():
        #    print(key,": ",value)
        dataId = aipkg['id']
        dataName = aipkg['name']
        aiDatasets[dataId] = dataName

def createDir(name):
    if not os.path.exists(name):
        try:
            os.makedirs(name)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

def downloadFile(url, name):
    try:
        urllib.request.urlretrieve(url, name)
    except Exception as e:
        print(str(e))


createDir(dataRootDir)
retrievePackages()

for Did,Dname in aiDatasets.items():
    print(Did,": ",Dname)
    datasetDir = dataRootDir+"/"+Dname
    createDir(datasetDir)
    Dpkg = dm.action.package_show(id=Did)
    #print(Dpkg)
    Dresources = Dpkg['resources']
    for res in Dresources:
        Rurl = res['url']
        Rname = res['name']
        print(Dname,": ",Rname,": ",Rurl)
        resFile = dataRootDir+"/"+Dname+"/"+Rname
        downloadFile(Rurl, resFile)


