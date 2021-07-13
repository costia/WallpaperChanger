
import requests
import logging
import base64
import json
import random
import os
from wx.core import INT64_MAX

from resources import Resources

class ImgurImageSource:
    def __init__(self,argsDict):
        self.log = logging.getLogger('WallpaperChanger')
        self.subreddit = argsDict['config']
        self.tempDir = Resources['TEMP_DIR']
        self.headerData = 'Q2xpZW50LUlEIDc0Mzg3MDdjODcwNDI1Yg=='
        self.APIendpoint = f'https://api.imgur.com/3/gallery/r/{self.subreddit}/'
        self.userAgent = str(random.randint(0,INT64_MAX))

    def getName(self):
        return '/r/'+self.subreddit
    
    @staticmethod
    def getTypeName():
        return 'imgur'

    def getImage(self):
        page = random.randint(0,100)
        response = requests.get(f'{self.APIendpoint}time/{page}', headers={'Authorization': base64.b64decode(self.headerData),'User-Agent':self.userAgent})
        response = json.loads(response.content)['data']
        assert(type(response)==list)
        postData = response[random.randint(0,len(response)-1)]
        assert(not postData['is_album'])

        id = postData['id']
        permalink = f'www.imgur.com/r/{self.subreddit}/{id}'

        response = requests.get(postData['link'])
        _,fileExtension = os.path.splitext(postData['link'])
        outFile = self.tempDir +'/downloaded'+ fileExtension
        f = open(outFile,'wb')
        for data in response:
            f.write(data)
        f.close()

        self.log.info(f'ImgurImageSource: {self.getName()} fetched {permalink}')

        retData = {
            'image':outFile,
            'metaName':postData['title'],
            'imageSource':permalink
        }
        return retData
