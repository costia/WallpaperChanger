
import requests
import logging
import base64
import json
import random
import os
from PIL import Image
from wx.core import INT64_MAX

from resources import Resources

class ImgurImageSource:
    def __init__(self,argsDict):
        self.log = logging.getLogger('WallpaperChanger')
        self.subreddit = argsDict['config']
        self.width = argsDict['width']
        self.height = argsDict['height']
        self.ARmargin = argsDict['aspectRatioMargin']
        self.minMP = self.width*self.height/2
        self.requiredAR = self.width/self.height

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

        im = Image.open(outFile)
        imWidth = im.size[0]
        imHeight = im.size[1]
        currentAR = imWidth/imHeight
        currentMP = imWidth*imHeight
        aspectRatioDiff =abs(currentAR-self.requiredAR)/self.requiredAR
        if aspectRatioDiff>self.ARmargin:
            self.log.error(f'RedditImageSource: {self.getName()} incompatible aspect ratio AR={currentAR} {permalink}')
            return None
        if currentMP<self.minMP:
            self.log.error(f'RedditImageSource: {self.getName()} small image {currentMP}MP {permalink}')
            return None

        retData = {
            'image':outFile,
            'metaName':postData['title'],
            'imageSource':permalink
        }
        return retData

        pass