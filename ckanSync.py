import json
import sys
import os, errno
import urllib
import urllib.error
import urllib.request
import configparser
import logging
from ckanapi import RemoteCKAN
import pkgsCache
ua = 'ckanapiexample/1.0 (+http://example.com/my/website)'

config = configparser.ConfigParser()
config.sections()
config.read('ckan.ini')
key = config['site']['key']
url = config['site']['url']
gDatasetList = config['dataset']['group']
oDatasetList = config['dataset']['organization']
dataRootDir = config['local']['data_root_directory']
dataSync = config['local'].getboolean('sync')
logFile = config['local']['logfile']
statusFile = config['local']['statusfile']
metaData = config['local']['metafile']

aiDatasets = {}
syncDatasets = {}

logging.basicConfig(filename=logFile,level=logging.DEBUG) ## INFO, WARNING

dm = RemoteCKAN(url, user_agent=ua, apikey=key)

def retrievePackages():
    if gDatasetList != '':
        pkgs = dm.action.group_show(id=gDatasetList,include_datasets=True)
    elif oDatasetList != '': #fixme
        pkgs = dm.action.organization_show(id=oDatasetList,include_datasets=True)

    aipkgs = pkgs['packages']

    for aipkg in aipkgs:
        dataId = aipkg['id']
        dataName = aipkg['name']
        aiDatasets[dataId] = dataName

def createDir(name):
    if not os.path.exists(name):
        try:
            os.makedirs(name)
        except OSError as e:
            if e.errno != errno.EEXIST:
                logging.error("create %s fail.(%s)!\n", name, str(e))
                raise

def downloadFile(url, name):
    try:
        urllib.request.urlretrieve(url, name)
    except Exception as e:
        logging.error("Sync %s to %s error.(%s)\n", url, name, str(e))

if __name__ == '__main__':

    md = pkgsCache.packages(metaData)
    createDir(dataRootDir)
    retrievePackages()
 
    pkg = ''
    if len(sys.argv) > 1:
        pkg = sys.argv[1]

    if pkg != '':
        for Did,Dname in aiDatasets.items():
            if Dname == pkg:
                syncDatasets[Did] = Dname
                break
    else:
        syncDatasets = aiDatasets

    for Did,Dname in syncDatasets.items():
        print("\n{0}".format(Dname))
        logging.debug("%s: %s\n",Did, Dname)
        datasetDir = dataRootDir+"/"+Dname
        createDir(datasetDir)
        Dpkg = dm.action.package_show(id=Did)
        logging.debug(Dpkg)
        Dresources = Dpkg['resources']
        for res in Dresources:
            logging.debug(res)
            rUrl = res['url']
            rName = res['name']
            rID = res['id']
            rRevision = res['revision_id']
            cRevision = md.getRevision(rID)
            if cRevision == rRevision and dataSync == True:
                print("\t", rName," skip")
                logging.debug("%s: %s: %s, skip", Dname, rName ,rUrl)
            else:
                print("\t", "%s downloading", rName)
                logging.debug("%s: %s: %s, downloading", Dname, rName ,rUrl)
                resFile = dataRootDir+"/"+Dname+"/"+rName
                md.cacheRevision(Did, rID, rRevision)
                downloadFile(rUrl, resFile)
