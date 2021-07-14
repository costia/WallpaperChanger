import requests
import logging
import base64
import os
import random
from bs4 import BeautifulSoup
import datetime

from resources import Resources

class FlickrImageSource:
    def __init__(self,argsDict):
        self.log = logging.getLogger('WallpaperChanger')
        self.tempDir = Resources['TEMP_DIR']
        self.paramData = 'P21ldGhvZD1mbGlja3IucGhvdG9zLnNlYXJjaCZhcGlfa2V5PWIxODM0N2FiYTkxNDlmYzlhMmM4NzhmYWJkMGY0YTFhJnRhZ3M9d2FsbHBhcGVyJmV4dHJhcz11cmxfbyZzb3J0PWludGVyZXN0aW5nbmVzcy1kZXNj'
        self.APIendpoint = f'https://api.flickr.com/services/rest/'
    
    def getName(self):
        return 'flickr'
    
    @staticmethod
    def getTypeName():
        return 'flickr'

    def getImage(self):
        pageNum = random.randint(0,40)
        dateLimit = int((datetime.datetime.utcnow() - datetime.timedelta(days=365)).timestamp())
        response = requests.get(f'{self.APIendpoint}{base64.b64decode(self.paramData).decode()}&page={pageNum}&min_taken_date={dateLimit}')
        response = BeautifulSoup(response.content,features='lxml')
        photos = response.find_all('photo')
        photos = list(filter(lambda x: 'url_o' in x.attrs,photos))
        selectedPhoto = photos[random.randint(0,len(photos)-1)].attrs
        
        response = requests.get(selectedPhoto['url_o'])
        _,fileExtension = os.path.splitext(selectedPhoto['url_o'])
        outFile = self.tempDir +'/downloaded'+ fileExtension
        f = open(outFile,'wb')
        for data in response:
            f.write(data)
        f.close()

        permalink = 'https://www.flickr.com/photos/'+selectedPhoto['owner']+'/'+selectedPhoto['id']
        self.log.info(f'ImgurImageSource: {self.getName()} fetched {permalink}')

        retData = {
            'image':outFile,
            'metaName':selectedPhoto['title'],
            'imageSource':permalink
        }
        return retData
