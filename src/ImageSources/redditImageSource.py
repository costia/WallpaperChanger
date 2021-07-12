import requests
import logging
import base64
import json
import random
import os
import threading
from urllib.parse import urlparse
from wx.core import INT64_MAX

from resources import Resources

class RedditPseudoRandomCacheThread(threading.Thread):
    def __init__(self,imageSource):
        super(RedditPseudoRandomCacheThread, self).__init__()
        self.imageSource = imageSource
        self.subreddit = imageSource.subreddit
        self.log = logging.getLogger('WallpaperChanger')
        self.tokenEndpoint = 'https://www.reddit.com/api/v1/access_token'
        self.APIendpoint = f'https://oauth.reddit.com/r/{self.subreddit}/'
        self.headerData = 'QmFzaWMgT1ROS04yWnNiRGhJTTB0c1NXWk9lVVJoYUhadWR6bz0='
        self.userAgent = str(random.randint(0,INT64_MAX))
    
    def getAllOfType(self,sortType,timeLimit,headers):
        aggregatedResponse = []
        params = {'limit':100,'t':timeLimit}
        apiEndpoint = self.APIendpoint+f'{sortType}.json'
        response = requests.get(apiEndpoint,headers=headers,params=params)
        response = json.loads(response.content)
        aggregatedResponse +=response['data']['children']
        followAfter = 5
        for _ in range(followAfter):
            afterTag = response['data']['after']
            if not afterTag:
                break
            params = {'limit':100,'t':timeLimit,'after':afterTag}
            response = requests.get(apiEndpoint,headers=headers,params=params)
            response = json.loads(response.content)
            aggregatedResponse +=response['data']['children']
        return aggregatedResponse

    def run(self):
        self.log.info(f'RedditPseudoRandomCacheThread: started {self.imageSource.getName()}')
        headers={'Authorization':base64.b64decode(self.headerData).decode(),'User-Agent':self.userAgent}
        params = {'grant_type':'https://oauth.reddit.com/grants/installed_client','device_id':'DO_NOT_TRACK_THIS_DEVICE'}
        response = requests.post(self.tokenEndpoint,headers=headers,params=params)
        response = json.loads(response.content)
        if 'access_token' not in response:
            self.log.error(f'RedditImageSource: {self.getName()} failed to get access token')
            return None
        accessToken=response['access_token']

        headers={'Authorization':f'Bearer {accessToken}','User-Agent':self.userAgent}

        aggregatedResponse = []
        aggregatedResponse += self.getAllOfType('top','month',headers)
        aggregatedResponse += self.getAllOfType('new','month',headers)
        aggregatedResponse += self.getAllOfType('rising','month',headers)
        aggregatedResponse += self.getAllOfType('hot','month',headers)
        aggregatedResponse = {x['data']['id']:x for x in aggregatedResponse}
        aggregatedResponse = list(aggregatedResponse.values())
        self.imageSource.pseudoRandomCache = aggregatedResponse
        self.log.info(f'RedditPseudoRandomCacheThread: finished {self.subreddit}')


class RedditImageSource:
    def __init__(self,argsDict):
        self.log = logging.getLogger('WallpaperChanger')
        self.subreddit = argsDict['config']
        self.width = argsDict['width']
        self.height = argsDict['height']
        self.ARmargin = argsDict['aspectRatioMargin']
        self.minMP = self.width*self.height/2
        self.requiredAR = self.width/self.height

        self.tempDir = Resources['TEMP_DIR']

        self.tokenEndpoint = 'https://www.reddit.com/api/v1/access_token'
        self.APIendpoint = f'https://oauth.reddit.com/r/{self.subreddit}/'
        self.APIendpointRandom = self.APIendpoint+'random.json'
        self.headerData = 'QmFzaWMgT1ROS04yWnNiRGhJTTB0c1NXWk9lVVJoYUhadWR6bz0='
        self.userAgent = str(random.randint(0,INT64_MAX))

    
    def getName(self):
        return '/r/'+self.subreddit
    
    @staticmethod
    def getTypeName():
        return 'subreddit'

    def getImage(self):
        headers={'Authorization':base64.b64decode(self.headerData).decode(),'User-Agent':self.userAgent}
        params = {'grant_type':'https://oauth.reddit.com/grants/installed_client','device_id':'DO_NOT_TRACK_THIS_DEVICE'}
        response = requests.post(self.tokenEndpoint,headers=headers,params=params)
        response = json.loads(response.content)
        if 'access_token' not in response:
            self.log.error(f'RedditImageSource: {self.getName()} failed to get access token')
            return None
        accessToken=response['access_token']
        headers={'Authorization':f'Bearer {accessToken}','User-Agent':self.userAgent}


        if not hasattr(self,'randSupported'):
            params = {'limit':1}
            response = requests.get(self.APIendpointRandom,headers=headers, params=params)
            parsedUrl = urlparse(response.url)
            self.randSupported = parsedUrl.path.startswith(f'/r/{self.subreddit}/comments/')
            if not self.randSupported:
                # https://stackoverflow.com/questions/60216514/unable-to-get-a-random-post-from-some-subreddits-with-praw
                self.log.warning(f'RedditImageSource: {self.getName()} does not support random fetch')
                self.pseudoRandomCache = None
                self.pseudoRandomCacheThread = RedditPseudoRandomCacheThread(self)
                self.pseudoRandomCacheThread.start()
                self.log.info(f'RedditImageSource: {self.getName()} building pseudo random cache')
                return None

        if self.randSupported:
            params = {'limit':1}
            response = requests.get(self.APIendpointRandom,headers=headers, params=params)
            parsedUrl = urlparse(response.url)
            response = json.loads(response.content)
            postData = response[0]['data']['children'][0]['data']
        else:
            if not self.pseudoRandomCache:
                assert(self.pseudoRandomCacheThread)
                self.pseudoRandomCacheThread.join(0)
                if not self.pseudoRandomCacheThread.is_alive():
                    self.pseudoRandomCacheThread = RedditPseudoRandomCacheThread(self)
                    self.pseudoRandomCacheThread.start()
                    self.log.info(f'RedditImageSource: {self.getName()} retrying building pseudo random cache')
                return None
            else:
                if self.pseudoRandomCacheThread:
                    self.pseudoRandomCacheThread.join(0)
                    if not self.pseudoRandomCacheThread.is_alive():
                        self.pseudoRandomCacheThread = None

            postData = self.pseudoRandomCache[random.randint(0,len(self.pseudoRandomCache)-1)]['data']

            # 1% chance to refresh cache
            if random.randint(0,100)==0:
                if not self.pseudoRandomCacheThread:
                    self.log.info(f'RedditImageSource: {self.getName()} refreshing pseudo random cache')
                    self.pseudoRandomCacheThread = RedditPseudoRandomCacheThread(self)
                    self.pseudoRandomCacheThread.start()

        permalink = 'www.reddit.com'+postData['permalink']
        if not 'post_hint' in postData or postData['post_hint']!='image':
            self.log.error(f'RedditImageSource: {self.getName()} unsupported post type {permalink}')
            return None
        
        imageData = postData['preview']['images'][0]['source']
        currentAR = imageData['width']/imageData['height']
        currentMP = imageData['width']*imageData['height']
        aspectRatioDiff =abs(currentAR-self.requiredAR)/self.requiredAR
        if aspectRatioDiff>self.ARmargin:
            self.log.error(f'RedditImageSource: {self.getName()} incompatible aspect ratio AR={currentAR} {permalink}')
            return None
        if currentMP<self.minMP:
            self.log.error(f'RedditImageSource: {self.getName()} small image {currentMP}MP {permalink}')
            return None
        
        response = requests.get(postData['url'])
        _,fileExtension = os.path.splitext(postData['url'])
        outFile = self.tempDir +'/downloaded'+ fileExtension
        f = open(outFile,'wb')
        for data in response:
            f.write(data)
        f.close()

        self.log.info(f'RedditImageSource: {self.getName()} fetched {permalink}')
        retData = {
            'image':outFile,
            'metaName':postData['title'],
            'imageSource':permalink
        }
        return retData
