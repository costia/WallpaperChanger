import requests
import logging
import base64
import json
import random
import os

from wx.core import INT64_MAX

class RedditImageSource:
    def __init__(self,argsDict):
        self.log = logging.getLogger('WallpaperChanger')
        self.subreddit = argsDict['subreddit']
        self.width = argsDict['width']
        self.height = argsDict['height']
        self.minMP = self.width*self.height/2
        self.requiredAR = self.width/self.height

        self.tempDir = os.path.abspath('./temp')
        if not os.path.isdir(self.tempDir):
            os.mkdir(self.tempDir)

        self.tokenEndpoint = 'https://www.reddit.com/api/v1/access_token'
        self.APIendpoint = f'https://oauth.reddit.com/r/{self.subreddit}/random.json?limit=1'
        self.headerData = 'QmFzaWMgT1ROS04yWnNiRGhJTTB0c1NXWk9lVVJoYUhadWR6bz0='
        self.userAgent = str(random.randint(0,INT64_MAX))
    
    def getImage(self):
        headers={'Authorization':base64.b64decode(self.headerData).decode(),'User-Agent':self.userAgent}
        params = {'grant_type':'https://oauth.reddit.com/grants/installed_client','device_id':'DO_NOT_TRACK_THIS_DEVICE'}
        response = requests.post(self.tokenEndpoint,headers=headers,params=params)
        response = json.loads(response.content)
        if 'access_token' not in response:
            self.log.error(f'RedditImageSource {self.subreddit} failed to get access token')
            return None
        accessToken=response['access_token']

        headers={'Authorization':f'Bearer {accessToken}','User-Agent':self.userAgent}
        response = requests.get(self.APIendpoint,headers=headers)
        response = json.loads(response.content)
        postData = response[0]['data']['children'][0]['data']
        permalink = postData['permalink']
        if not 'post_hint' in postData or postData['post_hint']!='image':
            self.log.error(f'RedditImageSource {self.subreddit} unsupported post type {permalink}')
            return None
        
        imageData = postData['preview']['images'][0]['source']
        currentAR = imageData['width']/imageData['height']
        currentMP = imageData['width']*imageData['height']
        if abs(currentAR-self.requiredAR)/self.requiredAR>0.1:
            self.log.error(f'RedditImageSource {self.subreddit} incompatible aspect ratio')
            return None
        if currentMP<self.minMP:
            self.log.error(f'RedditImageSource {self.subreddit} small image')
            return None
        
        response = requests.get(postData['url'])
        _,fileExtension = os.path.splitext(postData['url'])
        outFile = self.tempDir +'/downloaded'+ fileExtension
        f = open(outFile,'wb')
        for data in response:
            f.write(data)
        f.close()
        return outFile