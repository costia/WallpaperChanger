import requests
import logging
import base64
import json
import random
import os
from urllib.parse import urlparse
from wx.core import INT64_MAX

from resources import Resources


class RedditImageSource:
    def __init__(self,argsDict):
        self.log = logging.getLogger('WallpaperChanger')
        self.subreddit = argsDict['subreddit']
        self.width = argsDict['width']
        self.height = argsDict['height']
        self.minMP = self.width*self.height/2
        self.requiredAR = self.width/self.height

        self.tempDir = Resources['TEMP_DIR']

        self.tokenEndpoint = 'https://www.reddit.com/api/v1/access_token'
        self.APIendpoint = f'https://oauth.reddit.com/r/{self.subreddit}/'
        self.APIendpointRandom = self.APIendpoint+'random.json'
        self.APIendpointSearch = self.APIendpoint+'search.json'
        self.headerData = 'QmFzaWMgT1ROS04yWnNiRGhJTTB0c1NXWk9lVVJoYUhadWR6bz0='
        self.userAgent = str(random.randint(0,INT64_MAX))
    
    def getName(self):
        return self.subreddit

    def getImage(self):
        headers={'Authorization':base64.b64decode(self.headerData).decode(),'User-Agent':self.userAgent}
        params = {'grant_type':'https://oauth.reddit.com/grants/installed_client','device_id':'DO_NOT_TRACK_THIS_DEVICE'}
        response = requests.post(self.tokenEndpoint,headers=headers,params=params)
        response = json.loads(response.content)
        if 'access_token' not in response:
            self.log.error(f'RedditImageSource: {self.subreddit} failed to get access token')
            return None
        accessToken=response['access_token']

        headers={'Authorization':f'Bearer {accessToken}','User-Agent':self.userAgent}
        params = {'limit':1}
        response = requests.get(self.APIendpointRandom,headers=headers, params=params)
        parsedUrl = urlparse(response.url)
        if not parsedUrl.path.startswith(f'/r/{self.subreddit}/comments/'):
            # https://stackoverflow.com/questions/60216514/unable-to-get-a-random-post-from-some-subreddits-with-praw
            self.log.warning(f'RedditImageSource: {self.subreddit} does not support random fetch')
            sortTypes = ['relevance','hot','top','new','comments']
            sortType = sortTypes[random.randint(0,len(sortTypes)-1)]
            timeLimits = ['hour','day','week','month','year','all']
            timeLimit = timeLimits[random.randint(0,len(timeLimits)-1)]
            params = {'limit':100,'restrict_sr':1,'sort':sortType,'t':timeLimit}
            response = requests.get(self.APIendpoint,headers=headers,params=params)
            response = json.loads(response.content)
            response = response['data']['children']
            postData = response[random.randint(0,len(response)-1)]['data']
            pass
        else:
            response = json.loads(response.content)
            postData = response[0]['data']['children'][0]['data']
        permalink = 'www.reddit.com'+postData['permalink']
        if not 'post_hint' in postData or postData['post_hint']!='image':
            self.log.error(f'RedditImageSource: {self.subreddit} unsupported post type {permalink}')
            return None
        
        imageData = postData['preview']['images'][0]['source']
        currentAR = imageData['width']/imageData['height']
        currentMP = imageData['width']*imageData['height']
        if abs(currentAR-self.requiredAR)/self.requiredAR>0.1:
            self.log.error(f'RedditImageSource: {self.subreddit} incompatible aspect ratio {permalink}')
            return None
        if currentMP<self.minMP:
            self.log.error(f'RedditImageSource: {self.subreddit} small image {permalink}')
            return None
        
        response = requests.get(postData['url'])
        _,fileExtension = os.path.splitext(postData['url'])
        outFile = self.tempDir +'/downloaded'+ fileExtension
        f = open(outFile,'wb')
        for data in response:
            f.write(data)
        f.close()

        self.log.info(f'RedditImageSource: {self.subreddit} fetched {permalink}')
        return outFile