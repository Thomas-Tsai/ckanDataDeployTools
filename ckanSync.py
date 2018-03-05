import json
import os, errno
import urllib
import urllib.error
import urllib.request
import configparser
import logging
from ckanapi import RemoteCKAN
ua = 'ckanapiexample/1.0 (+http://example.com/my/website)'

config = configparser.ConfigParser()
config.sections()
config.read('ckan.ini')
key = config['site']['key']
url = config['site']['url']
dataRootDir = config['local']['data_root_directory']
dataSync = config['local']['sync']
logFile = config['local']['logfile']
statusFile = config['local']['statusfile']
metaData = config['local']['metafile']

aiDatasets = {}

logging.basicConfig(filename=logFile,level=logging.DEBUG) ## INFO, WARNING

dm = RemoteCKAN(url, user_agent=ua, apikey=key)

def retrievePackages():
    pkgs = dm.action.group_show(id="ai",include_datasets=True)
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
