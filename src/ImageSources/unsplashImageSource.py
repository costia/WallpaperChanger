import requests
import logging
import urllib.parse as urlparse
from urllib.parse import parse_qs

from resources import Resources

class UnsplashImageSource:
    def __init__(self,argsDict):
        self.log = logging.getLogger('WallpaperChanger')
        self.tempDir = Resources['TEMP_DIR']
        self.APIendpoint = 'http://source.unsplash.com/random/'
        self.resolutionString = '1920x1080'
        self.photoAPIendpoint = 'https://images.unsplash.com'

    def getName(self):
        return 'unsplash'
    
    @staticmethod
    def getTypeName():
        return 'unsplash'

    def getImage(self):
        response =  requests.get(self.APIendpoint+self.resolutionString)
        parsedUrl = urlparse.urlparse(response.url)
        urlParams = parse_qs(parsedUrl.query)
        fileExtension = '.'+urlParams['fm'][0]

        permalink = self.photoAPIendpoint+parsedUrl.path
        response =  requests.get(permalink)
        outFile = self.tempDir +'/downloaded'+ fileExtension
        f = open(outFile,'wb')
        for data in response:
            f.write(data)
        f.close()

        self.log.info(f'UnsplashImageSource: {self.getName()} fetched {permalink}')

        retData = {
            'image':outFile,
            'metaName':urlParams['ixid'][0],
            'imageSource':permalink
        }
        return retData