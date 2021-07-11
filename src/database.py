import sqlite3
import logging
from resources import Resources
import datetime
import hashlib
import os

class WallpaperDatabase:
    def __init__(self):
        self.log = logging.getLogger('WallpaperChanger')

        db = sqlite3.connect(Resources['DB_FILE'])
        cursor = db.cursor()
        cursor.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="history"')
        res = cursor.fetchone()
        if not res :
            sql = 'CREATE TABLE "history" ("ID"	INTEGER NOT NULL UNIQUE,"sourceType" TEXT NOT NULL,' 
            sql += '"sourceName"	TEXT NOT NULL, "imageName"	TEXT NOT NULL,"imageSource"	TEXT NOT NULL, '
            sql += '"imageMD5"	TEXT NOT NULL, "imageSize"	TEXT NOT NULL, "date" NUMERIC NOT NULL, PRIMARY KEY("ID" AUTOINCREMENT));'
            cursor.execute(sql)
            db.commit()
        db.close()

    def addEntry(self,entryDict):
        db = sqlite3.connect(Resources['DB_FILE'])
        imageSize = os.path.getsize(entryDict['image'])
        imageMD5 = self._fileMD5(entryDict['image'])
        sql = 'INSERT INTO history(sourceType,sourceName,imageName,imageSource,imageMD5,imageSize,date)  VALUES(?,?,?,?,?,?,?)'
        data =(entryDict['sourceType'], entryDict['sourceName'], entryDict['imageName'], entryDict['imageSource'], imageMD5,imageSize,datetime.datetime.utcnow().timestamp())
        cursor = db.cursor()
        cursor.execute(sql,data)
        db.commit()
        db.close()

    def _fileMD5(self, filename):
        hash_md5 = hashlib.md5()
        f = open(filename,'rb')
        while data:=f.read(1024**2):
            hash_md5.update(data)
        f.close()
        return hash_md5.hexdigest()

    def getLatest(self,count):
        db = sqlite3.connect(Resources['DB_FILE'])
        cursor = db.cursor()
        sql = 'SELECT imageName,imageSource,date FROM history ORDER BY date DESC LIMIT ?'
        cursor.execute(sql,(count,))
        res = cursor.fetchall()
        names = [x[0] for x in res]
        sources = [x[1] for x in res]
        db.close()
        return names, sources


    def checkDuplicate(self,image):
        ret = None
        time = datetime.datetime.utcnow() - datetime.timedelta(days=30)
        time = time.timestamp()
        imageSize = os.path.getsize(image)
        
        db = sqlite3.connect(Resources['DB_FILE'])
        cursor = db.cursor()

        sql = 'SELECT * FROM history WHERE imageSize=? AND date>?'
        cursor.execute(sql,(imageSize,time))
        res = cursor.fetchone()
        if res:
            imageMD5 = self._fileMD5(image)
            sql = 'SELECT * FROM history WHERE imageMD5=? AND date>?'
            cursor.execute(sql,(imageMD5,time))
            res = cursor.fetchone()
            if res:
                ret=res[1]+':'+res[4]
        db.close()
        return ret
        


        

