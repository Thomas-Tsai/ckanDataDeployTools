import json
import sys
import os, errno
import urllib
import urllib.error
from urllib.error import URLError, HTTPError
import urllib.request
import configparser
import logging
from ckanapi import RemoteCKAN
import pkgsCache
import cgi
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

def retrievePackages(dataset=''):
    if dataset == '':
        if gDatasetList != '':
            pkgs = dm.action.group_show(id=gDatasetList,include_datasets=True)
        elif oDatasetList != '': #fixme, should merge group and organization together
            pkgs = dm.action.organization_show(id=oDatasetList,include_datasets=True)
        aipkgs = pkgs['packages']

        for aipkg in aipkgs:
            dataId = aipkg['id']
            dataName = aipkg['name']
            aiDatasets[dataId] = dataName
    else:
        pkg = dm.action.package_show(id=dataset)
        dataId = pkg['id']
        dataName = pkg['name']
        aiDatasets[dataId] = dataName

def createDir(name):
    if not os.path.exists(name):
        try:
            os.makedirs(name)
        except OSError as e:
            if e.errno != errno.EEXIST:
                logging.error("create %s fail.(%s)!\n", name, str(e))
                raise

def downloadFile(url, rootDir, dataset, resource):
    opener = urllib.request.build_opener()
    opener.addheaders = [('Authorization', key)]
    try: 
        remotefile = opener.open(url)
        rfileinfo = remotefile.info()['Content-Disposition']
        r_value, r_params = cgi.parse_header(rfileinfo)
    except HTTPError as e:
        logging.error('The server couldn\'t fulfill the request.')
        logging.error('Error code: ', e.code)
        print('Error code: ', e.code)
        return False
    except URLError as e:
        logging.error('We failed to reach a server.')
        logging.error('Reason: ', e.reason)
        print('Reason: ', e.reason)
        return False
    if "filename" in r_params:
        resource = r_params["filename"]
    name = rootDir+"/"+dataset+"/"+resource
    print("to {}".format(name))
    try:
        urllib.request.install_opener(opener)
        urllib.request.urlretrieve(url, name)
        return True
    except Exception as e:
        logging.error("Sync %s to %s error.(%s)\n", url, name, str(e))
        return False

    return False

def checkFile(Dname, rName):
    DnamePath = dataRootDir+"/"+Dname
    rNamePath = DnamePath+"/"+rName
    if os.path.isdir(DnamePath) == True:
        if os.path.exists(rNamePath):
            return True
    return False

if __name__ == '__main__':

    md = pkgsCache.packages(metaData)
    createDir(dataRootDir)
    pkg = ''
    if len(sys.argv) > 1:
        pkg = sys.argv[1]

    retrievePackages(pkg)

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
            fileExist = checkFile(Dname, rName)
            if cRevision == rRevision and dataSync == True and fileExist == True:
                print("\t", rName," skip")
                logging.debug("%s: %s: %s, skip", Dname, rName ,rUrl)
            else:
                print("\t Download {} ".format(rName), end = '')
                logging.debug("%s: %s: %s, downloading", Dname, rName ,rUrl)
                if downloadFile(rUrl, dataRootDir, Dname, rName) == True:
                    md.cacheRevision(Did, rID, rRevision)
