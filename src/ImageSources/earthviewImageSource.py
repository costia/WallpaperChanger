import requests
import logging
from bs4 import BeautifulSoup
import json
import os

from resources import Resources

class EarthviewImageSource:
    def __init__(self,argsDict):
        self.log = logging.getLogger('WallpaperChanger')
        response = requests.get('https://earthview.withgoogle.com/')
        htmldata = BeautifulSoup(response.content.decode(),features="html.parser")
        firstID = json.loads(htmldata.find('body')['data-photo'])
        self.nextId = firstID['nextSlug']
        self.tempDir = Resources['TEMP_DIR']

    def getName(self):
        return 'earthview'
    
    @staticmethod
    def getTypeName():
        return 'earthview'

    def getImage(self):
        response = requests.get(f'https://earthview.withgoogle.com/_api/{self.nextId}.json')
        postData = json.loads(response.content)
        self.nextId = postData['nextSlug']

        response = requests.get(postData['photoUrl'])
        _,fileExtension = os.path.splitext(postData['photoUrl'])
        outFile = self.tempDir +'/downloaded'+ fileExtension
        f = open(outFile,'wb')
        for data in response:
            f.write(data)
        f.close()

        self.log.info(f'EarthviewImageSource: selected file is {outFile}')
        retData = {
            'image':outFile,
            'metaName':postData['name'],
            'imageSource':postData['shareUrl']
        }
        return retData
