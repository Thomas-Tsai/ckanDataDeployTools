import sqlite3
import sys
import os, errno
import logging
import configparser

config = configparser.ConfigParser()
config.sections()
config.read('ckan.ini')
logFile = config['local']['logfile']

logging.basicConfig(filename=logFile,level=logging.DEBUG) ## INFO, WARNING

class packages:

    def __init__(self, sqlFile):
    
        self.myDBVersion = '0.1'
        self.sqlFileName = sqlFile
        self.conn = ''
        self.cursor = ''
        if self.checkFilename(sqlFile) == True:
            self.conn = sqlite3.connect(self.sqlFileName)
            self.cursor = self.conn.cursor()
        else:
            self.initDB()

        self.checkDatabaseVersion()

    def checkFilename(self, filename):
        if filename is not None:
            if os.path.exists(filename):
                return True

    def checkDatabaseVersion(self):
        self.cursor.execute('''select * from ckansync''')
        vRow = self.cursor.fetchone()
        if vRow[1] < self.myDBVersion:
            print("version outofdate")
        else:
            print('db version ok')
            
    #print("need migration, but not yet support\n")
    #return 

    def initDB(self):
        self.conn = sqlite3.connect(self.sqlFileName)
        self.cursor = self.conn.cursor()
        # Create table
        self.cursor.execute('''CREATE TABLE ckansync (ckanSyncVersion text, ckanSyncDBVersion text, lastUpdateTime REAL DEFAULT ( DATETIME('now', 'localtime')))''')
        #c.execute('''CREATE TABLE packages (pkgId text, pkgName text, pkgVid text, pkgUrl text, pkgFileName text)''')
        self.cursor.execute('''CREATE TABLE synccache (pkgID text, resID text, resRevision text, lastUpdateTime REAL DEFAULT ( DATETIME('now', 'localtime')))''')

        self.cursor.execute("INSERT INTO ckansync(ckanSyncVersion,ckanSyncDBVersion) VALUES ('0.2', '0.1')")

        # Save (commit) the changes
        self.conn.commit()


    def addPkgData(self, pkgid, rid, revision):

        sql = "INSERT INTO synccache(pkgID, resID, resRevision) VALUES ('{0}', '{1}', '{2}')".format(pkgid, rid, revision)
        logging.error(sql)
        self.cursor.execute(sql)
        # Save (commit) the changes
        self.conn.commit()

    def getRevision(self, rid):
        sql = "select resRevision from synccache where resID='{0}'".format(rid)
        logging.error(sql)
        self.cursor.execute(sql)
        vRow = self.cursor.fetchone()
        logging.error(vRow)
        if vRow is None:
            return 0
        return vRow[0]

    def updateRevision(self, rid, revision):
        sql = "UPDATE synccache SET resRevision='{1}' where resID='{0}'".format(rid, revision)
        logging.error(sql)
        self.cursor.execute(sql)
        self.conn.commit()

    def cacheRevision(self, pkgid, rid, revision):
        self.updateRevision(rid, revision)
        if self.cursor.rowcount == 0:
            self.addPkgData(pkgid, rid, revision)

    def close(self):
        self.conn.close()
    #def delPkgData(self, pkgid, rid, revision):

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
