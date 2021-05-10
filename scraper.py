from logging import warn
import math
import requests
import wget
import shutil
import os
import json
import datetime
import time
import random
import praw
import instaloader
import youtube_dl
import tweepy

#text colors
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

#------ start funcs
def writeLog(message, type):
     if loggingLevel == 0:
          return
     if type.upper() == "ERROR" and loggingLevel >= 1:
          print(bcolors.FAIL,"ERROR:",message,bcolors.ENDC)
          global errors
          errors+=1
     elif type.upper() == "WARNING" and loggingLevel >= 2:
          print(bcolors.WARNING,"WARNING:",message,bcolors.ENDC)
          global warnings
          warnings+=1
     elif type.upper() == "INFO" and loggingLevel >= 3:
          print("\033[1;37;40mINFO:",message,bcolors.ENDC)

#user specific
def getImage(filename):
     #print("in getImage")
     #catch gifv links to get special parsing
     if filename.split(".")[-1] == "gifv":
          getGIFV(filename=filename)
          return
     #build filename for local write
     filename = submission.url.split("/")[-1]
     filename = filename.replace("?","")
     filename = userpath+str(subcount)+"-"+user.name+"-"+filename
     #check if file exists - do not overwrite if it does
     if  os.path.exists(filename):
          m="File already exists -"+filename
          writeLog(message=m,type="WARNING")
          return
     # Open the url image, set stream to True, this will return the stream content.
     r = requests.get(submission.url, stream = True)
     # Check if the image was retrieved successfully
     if r.status_code == 200:
          # Set decode_content value to True, otherwise the downloaded image file's size will be zero.
          r.raw.decode_content = True
          # Open a local file with wb ( write binary ) permission.
          with open(filename,'wb') as f:
               shutil.copyfileobj(r.raw, f)
          m="Image sucessfully Downloaded: "+filename
          writeLog(message=m,type="INFO")
     else:
          m="Image Couldn\'t be retreived: "+submission.url+" CODE: "+str(r.status_code)
          writeLog(message=m,type="ERROR")

def getGIF(filename):
     #print("in getGIF")
     return

def getGIFV(filename):
     #print("in getGIFV")
     lastSlashIndex = filename.rfind("/")
     newFilename = filename[:lastSlashIndex]+filename.split("/")[-1].split(".")[0] + ".mp4"
     m="changed <"+filename+"> to <"+newFilename+">"
     writeLog(message=m,type="INFO")
     getImage(filename=newFilename)

def getGallery(filename):
     #print("in getGallery")
     m="getting gallery from "+filename
     writeLog(message=m,type="INFO")

def getSubredditImage(filename):
     #print("in getSubredditImage")
     #catch gifv links to get special parsing
     if filename.split(".")[-1] == "gifv":
          getGIFV(filename=filename)
          return
     #build filename for local write
     filename = url.split("/")[-1]
     filename = filename.replace("?","")
     filename = subpath+str(subcount)+"-"+subname+"-"+filename
     #check if file exists - do not overwrite if it does
     if  os.path.exists(filename):
          m="File already exists -"+filename
          writeLog(message=m,type="WARNING")
          return
     # Open the url image, set stream to True, this will return the stream content.
     r = requests.get(url, stream = True)
     # Check if the image was retrieved successfully
     if r.status_code == 200:
          # Set decode_content value to True, otherwise the downloaded image file's size will be zero.
          r.raw.decode_content = True
          # Open a local file with wb ( write binary ) permission.
          with open(filename,'wb') as f:
               shutil.copyfileobj(r.raw, f)
          m="Image sucessfully Downloaded: "+filename
          writeLog(message=m,type="INFO")
     else:
          m="Image Couldn\'t be retreived: "+url+" CODE: "+str(r.status_code)
          writeLog(message=m,type="ERROR")

#subreddit specific
def getSubredditGIF(filename):
     #print("in getSubredditGIF")
     return

def getSubredditGIFV(filename):
     #print("in getSubredditSubredditGIFV")
     lastSlashIndex = filename.rfind("/")
     newFilename = filename[:lastSlashIndex]+"/"+filename.split("/")[-1].split(".")[0] + ".mp4"
     m="changed <"+filename+"> to <"+newFilename+">"
     writeLog(message=m,type="INFO")
     getSubredditImage(filename=newFilename)

def getSubredditGallery(filename):
     #print("in getSubredditGallery")
     m="getting gallery from "+filename
     writeLog(message=m,type="INFO")

#prep data from settings json
def processScrapeList(_scrapeList, _userList, _subList, _instaList,_instaAccountList,_twitList,_twitterUsersList,_subredSkip,_redditorSkip,_instaSkip,_twitSkip):
     if not _redditorSkip and not _subredSkip:
          for item in _scrapeList:
               if item.split("/")[0] == 'r' and not item.split("/")[1] in _subList and not _subredSkip:
                    m="[Subreddit] processing new sub: "+item
                    writeLog(message=m,type="INFO")
                    _subList.append(item.split("/")[1])
               elif item.split("/")[0] == 'u' and not item.split("/")[1] in _userList and not _redditorSkip:
                    m="[Redditor] processing new user: "+item
                    writeLog(message=m,type="INFO")
                    _userList.append(item.split("/")[1])
               elif item.split("/")[1] in _userList or item.split("/")[1] in _subList:
                    writeLog("duplicate item provided "+item,type="WARNING")
               else:
                    writeLog("invalid account provided "+item,type="WARNING")
          if not _redditorSkip:
               _userList.sort()
          if not _subredSkip:
               _subList.sort()
     if not _instaSkip:
          for item in  _instaList:
               if item in _instaAccountList:
                    writeLog("duplicate item provided "+item,type="WARNING")
                    continue
               m="[Instagram] processing new user: "+item
               writeLog(message=m,type="INFO")
               _instaAccountList.append(item)
          random.shuffle(_instaAccountList) #random shuffle to try to rotate through rate limiting
     if not _twitSkip:
          for item in _twitList:
               if item in _twitterUsersList:
                    writeLog("duplicate item provided "+item,type="WARNING")
                    continue
               m="[Twitter] processing new user: "+item
               writeLog(message=m,type="INFO")
               _twitterUsersList.append(item)
          _twitterUsersList.sort()     

@classmethod
def parse(cls, api, raw):
     status = cls.first_parse(api, raw)
     setattr(status, 'json', json.dumps(raw))
     return status

#----- end funcs

startTime = datetime.datetime.now()
os.system('color')
scriptdir = os.path.dirname(os.path.realpath(__file__))
#read ./settings.json
with open(scriptdir+"/dev.settings.json") as settingsFile: #!!!CHANGE THIS BACK TO DEFAULT TO settings.json!!!
     settings = json.load(settingsFile)     

red_clientID = settings["red_clientID"] #reddit app client id for praw
red_clientSecret = settings["red_clientSecret"] #reddit app client secret for praw
red_userAgent = settings["red_agentName"] #reddit app user agent name for praw
twit_consKey= settings["twit_consKey"]
twit_consSec= settings["twit_consSec"]
twit_bearTok = settings["twit_bearerTok"]
scrapeList = settings["scrapeList"] #raw scrape list for reddit accounts/subs
imageDomains = settings["imageDomains"] #whitelist of domains to pull images from
gifDomains = settings["gifDomains"] #whitelist of domains to pull gifs from
videoDomains = settings["videoDomains"] #whitelist of domains to pull videos from
rootPath = settings["destination"] #root path to download to
loggingLevel = settings["loggingLevel"] #0 no logging, 1 error logging, 2 warning logging, 3 info logging
if loggingLevel > 3:
     loggingLevel = 3
if loggingLevel < 0:
     loggingLevel = 0
instaList = settings["instaList"] #list of insta accounts to scrape
twitList = settings["twitterList"]
subredSkip = settings["subRedditSkip"] #skip subreddit scrapes?
redditorSkip = settings["redditorSkip"] #skip redditor scrapes?
instaSkip = settings["instaSkip"] #skip insta scrapes?
twitSkip = settings["twitSkip"] #skip twitter scrapes?
userList = [] #processed list of reddit users
subList = [] #processed listof subreddits
instaAccounts = [] #processed list of instagram accounts
twitUserList = [] #processed list of twitter users
#stats for logging
captured = 0
warnings=0
errors = 0
tweetsSeen = 0


#setup user and subreddit lists
processScrapeList(_scrapeList=scrapeList,_userList=userList,_subList=subList, _instaList = instaList, _instaAccountList=instaAccounts, _twitList = twitList, _twitterUsersList= twitUserList,_subredSkip=subredSkip,_redditorSkip=redditorSkip,_instaSkip=instaSkip,_twitSkip=twitSkip)

#praw reddit client setup
if not subredSkip or not redditorSkip:
     reddit = praw.Reddit(client_id=red_clientID, client_secret=red_clientSecret, user_agent=red_userAgent)

if not redditorSkip:
     #loop through all reddit users to pull content
     for username in userList:
          #try to get user - continue to next if error
          try:
               user = reddit.redditor(username)
               m="getting user "+user.name
               writeLog(message=m,type="INFO")
          except:
               m="Failed to get user: "+username
               writeLog(message=m,type="ERROR")
               continue
          #setup path to write files to
          userpath = rootPath+user.name+"/"
          m="writing this user content to - "+userpath
          writeLog(message=m,type="INFO")
          #create base path per username scraped
          try:
               os.makedirs(os.path.dirname(userpath), exist_ok=True)
          except:
               m = "Failed to create directory: "+userpath
               writeLog(message=m,type="ERROR")
               continue
          #try to get all submissions from a user
          try:
               submissions = user.submissions.top("all")
          except:
               m="couldnt get top submissions - "+user.name
               writeLog(message=m,type="ERROR")
               continue
          subcount = 0
          for submission in submissions:
               captured+=1
               subcount+= 1
               #convert imgur.com links into i.imgur.com links
               if submission.domain == "imgur.com":
                    modURL = submission.url
                    modURL = "i.imgur.com/a/"+modURL.split("/")[-1]
                    m="changed <"+submission.url+"> to <"+modURL+">"
                    writeLog(message=m,type="INFO")
                    m= "getting [",user.name,"] "+submission.title+" "+modURL
                    writeLog(message=m,type="INFO")
                    getImage(filename=modURL)
                    continue

               #parse gifv and kick off  gifv grabbing
               if submission.url.split(".")[-1] == "gifv":
                    #print("got a gifv")
                    getGIFV(filename=submission.url)
                    continue
               
               #download items from video domains using youtube-dl
               if submission.domain in videoDomains:
                    m="getting ["+user.name+"] "+submission.title+" "+submission.url
                    writeLog(message=m,type="INFO")
                    filename = submission.url.split("/")[-1]
                    filename = filename.replace("?","")
                    filename = userpath+str(subcount)+"-"+user.name+"-"+filename
                    if  os.path.exists(filename):
                         m="File already exists -"+filename
                         writeLog(message=m,type="WARNING")
                         continue
                    ydl_opts = {
                         'format':'best',
                         'outtmpl': filename,
                         'cachedir': False,
                         'force_generic_extractor': (submission.domain in videoDomains or submission.domain in gifDomains),
                         'quiet':(loggingLevel <= 2),
                         'no_warnings': (loggingLevel < 2)
                    }
                    print(bcolors.OKBLUE,end="")
                    try:
                         with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                              ydl.download([submission.url])
                    except:
                         writeLog(message="failed to download video - "+submission.url+" "+submission.domain,type="ERROR")
                    print(bcolors.ENDC,end="")
                    continue

               if "gallery" in submission.url and submission.domain == "reddit.com":
                    getGallery(filename=submission.url)
                    continue

               #standard image grab
               if(not submission.is_self and submission.domain in imageDomains):
                    m="getting ["+user.name+"] "+submission.title+" "+submission.url
                    writeLog(message=m,type="INFO")
                    getImage(filename=submission.url)
               #gif grab
               elif(not submission.is_self and submission.domain in gifDomains):
                    m="getting ["+user.name+"] "+submission.title+" "+submission.url+" "+submission.domain
                    writeLog(message=m,type="INFO")
                    getGIF(filename=submission.url)
               #case to catch all other items
               else:
                    m = "NOT IMAGE - "+submission.title+" "+submission.url+" "+submission.domain
                    writeLog(message=m,type="WARNING")
                    continue

if not subredSkip:
     #loop through all subreddits to pull content
     #takes advantage of pushshift api
     for subname in subList:
          query = "https://api.pushshift.io/reddit/search/submission/?subreddit="+subname+"&sort=desc&sort_type=created_utc&before="+str(round(time.time()))+"&size=1000"
          m="requesting "+query
          writeLog(message=m, type="INFO")
          r = requests.get(query, stream = True)
          if r.status_code == 200:
               data = r.json()
          else:
               m="query for "+subname+" couldn't be processed... CODE"+str(r.status_code)
               writeLog(message=m,type="ERROR")
               continue
          #setup path to write files to
          subpath = rootPath+subname+"/"
          m="writing this subreddit content to - "+subpath
          writeLog(message=m,type="INFO")
          #create base path per username scraped
          try:
               os.makedirs(os.path.dirname(subpath), exist_ok=True)
          except:
               m = "Failed to create directory: "+subpath
               writeLog(message=m,type="ERROR")
               continue
          #try to get all submissions from a user
          subcount = 0
          for submission in data.get("data"):
               captured+=1
               subcount+= 1
               url = submission["url"]
               #convert imgur.com links into i.imgur.com links
               if submission["domain"] == "imgur.com":
                    modURL = url
                    modURL = "i.imgur.com/a/"+modURL.split("/")[-1]
                    m="changed <"+url+"> to <"+modURL+">"
                    writeLog(message=m,type="INFO")
                    m= "getting [",subname,"] "+submission["title"]+" "+modURL
                    writeLog(message=m,type="INFO")
                    getSubredditImage(filename=modURL)
                    continue

               #parse gifv and kick off  gifv grabbing
               if url.split(".")[-1] == "gifv":
                    #print("got a gifv")
                    getSubredditGIFV(filename=url)
                    continue
               
               #download items from video domains using youtube-dl
               if submission["domain"] in videoDomains:
                    m="getting ["+subname+"] "+submission["title"]+" "+url
                    writeLog(message=m,type="INFO")
                    filename = url.split("/")[-1]
                    filename = filename.replace("?","")
                    filename = subpath+str(subcount)+"-"+subname+"-"+filename
                    if  os.path.exists(filename):
                         m="File already exists -"+filename
                         writeLog(message=m,type="WARNING")
                         continue
                    ydl_opts = {
                         'format':'best',
                         'outtmpl': filename,
                         'cachedir': False,
                         'force_generic_extractor': (submission["domain"] in videoDomains or submission["domain"] in gifDomains),
                         'quiet':(loggingLevel <= 2),
                         'no_warnings': (loggingLevel < 2)
                    }
                    print(bcolors.OKBLUE,end="")
                    try:
                         with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                              ydl.download([url])
                    except:
                         writeLog(message="failed to download video - "+url+" "+submission["domain"],type="ERROR")
                    print(bcolors.ENDC,end="")
                    continue

               if "gallery" in url and submission["domain"] == "reddit.com":
                    getSubredditGallery(filename=url)
                    continue

               #standard image grab
               if(not submission["is_self"] and submission["domain"] in imageDomains):
                    m="getting ["+subname+"] "+submission["title"]+" "+url
                    writeLog(message=m,type="INFO")
                    getSubredditImage(filename=url)
               #gif grab
               elif(not submission["is_self"] and submission["domain"] in gifDomains):
                    m="getting ["+subname+"] "+submission["title"]+" "+submission["url"]+" "+submission["domain"]
                    writeLog(message=m,type="INFO")
                    getSubredditGIF(filename=url)
               #case to catch all other items
               else:
                    m = "NOT IMAGE - "+submission["title"]+" "+url+" "+submission["domain"]
                    writeLog(message=m,type="WARNING")
                    continue

if not instaSkip:
     #loop through all insta profiles to scrape content
     for profile in instaList:
          userpath = rootPath+profile+"/"
          m="writing this user content to - "+userpath
          writeLog(message=m,type="INFO")
          #create base path per username scraped
          try:
               os.makedirs(os.path.dirname(userpath), exist_ok=True)
          except:
               m = "Failed to create directory: "+userpath
               writeLog(message=m,type="ERROR")
               continue
          mod=instaloader.Instaloader(dirname_pattern=userpath,download_video_thumbnails=False)
          m="Attempting to download "+profile
          writeLog(message=m,type="INFO")
          try:
               mod.download_profile(profile)
          except:
               m="exception thrown when processing "+profile
               writeLog(message=m, type="ERROR")

if not twitSkip:
     # Status() is the data model for a tweet
     tweepy.models.Status.first_parse = tweepy.models.Status.parse
     tweepy.models.Status.parse = parse
     # User() is the data model for a user profil
     tweepy.models.User.first_parse = tweepy.models.User.parse
     tweepy.models.User.parse = parse
     # You need to do it for all the models you need
     auth = tweepy.AppAuthHandler(twit_consKey, twit_consSec)
     twitter = tweepy.API(auth)
     for user in twitUserList:
          twitUserpath = rootPath+user+"/"
          m="writing this twitter user content to - "+twitUserpath
          writeLog(message=m,type="INFO")
          try:
               os.makedirs(os.path.dirname(twitUserpath), exist_ok=True)
          except:
               m = "Failed to create directory: "+twitUserpath
               writeLog(message=m,type="ERROR")
               continue

          #get all tweets
          allTweets = []
          newTweets = twitter.user_timeline(screen_name = user,count=200,include_rts=False)
          allTweets.extend(newTweets)
          count=0
          while len(newTweets) > 0:
               writeLog(f"[{(200*count)+200}]Getting next set of tweets...","INFO")
               newTweets = twitter.user_timeline(screen_name = user,count=200,include_rts=False,max_id=allTweets[-1].id - 1)
               allTweets.extend(newTweets)
               count+=1
          tweetsSeen+=len(allTweets)
          #parse all tweets for media links
          mediaFiles = []
          for tweet in allTweets:
               tweetAsJSON = json.loads(tweet.json)
               try:
                    if len(tweetAsJSON["entities"]["media"]) > 0:
                         for m in tweetAsJSON["entities"]["media"]:
                              mediaFiles.append(m["media_url"])
               except:
                    twtID = tweetAsJSON["id"]
                    twtLink = f"https://twitter.com/{user}/status/{twtID}"
                    writeLog(f"Tweet (ID: {twtID} | Link: {twtLink}) didn't have a media entity key","WARNING")
          
          #download all media links
          mediaCount =0
          for mediaFile in mediaFiles:
               mediaCount+=1
               #build filename for local write
               filename = mediaFile.split("/")[-1]
               filename = filename.replace("?","")
               filename = twitUserpath+str(mediaCount)+"-"+user+"-"+filename
               #check if file exists - do not overwrite if it does
               if  os.path.exists(filename):
                    m="File already exists -"+filename
                    writeLog(message=m,type="WARNING")
                    continue
               try:
                    writeLog(f"\n[{user}] Attempting to download {mediaFile}","INFO")
                    wget.download(mediaFile,out=filename)
                    captured+=1
               except:
                    writeLog(f"\nFailed to download {mediaFile}","ERROR")

print() #try to fix weird same line issue with wget output

m=("\033[1;32;40mDownloaded: "+str(captured)+"\nRedditors: "+str(len(userList))+"\nSubreddits: "+str(len(subList))+"\nInsta Accounts: "+str(len(instaList))+"\nTwitter Accounts: "+str(len(twitUserList))+"\nTweets seen: "+str(tweetsSeen)+"\nDuration: "+str(datetime.timedelta(seconds=math.floor((datetime.datetime.now() - startTime).total_seconds()))))
if loggingLevel >=2:
     m+="\nWarnings:"+str(warnings)
if loggingLevel >=1:
     m+="\nErrors:"+str(errors)
m+=bcolors.ENDC
writeLog(m,"INFO")
