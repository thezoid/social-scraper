from logging import warn
import requests
import shutil
import os
import json
import datetime
import time
import random
import praw
import instaloader
import youtube_dl

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
     newFilename = filename[:lastSlashIndex]+filename.split("/")[-1].split(".")[0] + ".mp4"
     m="changed <"+filename+"> to <"+newFilename+">"
     writeLog(message=m,type="INFO")
     getImage(filename=newFilename)

def getSubredditGallery(filename):
     #print("in getSubredditGallery")
     m="getting gallery from "+filename
     writeLog(message=m,type="INFO")

#prep data from settings json
def processScrapeList(_scrapeList, _userList, _subList, _instaList,_instaAccountList):
     for item in _scrapeList:
          if item.split("/")[0] == 'r' and not item.split("/")[1] in _subList:
               m="processing new sub: "+item
               writeLog(message=m,type="INFO")
               _subList.append(item.split("/")[1])
          elif item.split("/")[0] == 'u' and not item.split("/")[1] in _userList:
               m="processing new user: "+item
               writeLog(message=m,type="INFO")
               _userList.append(item.split("/")[1])
          elif item.split("/")[1] in _userList or item.split("/")[1] in _subList:
               writeLog("duplicate item provided "+item,type="WARNING")
          else:
               writeLog("invalid account provided "+item,type="WARNING")
     for item in  _instaList:
          _instaAccountList.append(item)
     _userList.sort()
     _subList.sort()
     random.shuffle(_instaAccountList) #random shuffle to try to rotate through rate limiting

#----- end funcs

startTime = datetime.datetime.now()
#read ./settings.json
with open("dev.settings.json") as settingsFile: #!!!CHANGE THIS BACK TO DEFAULT TO settings.json!!!
     settings = json.load(settingsFile)     

clientID = settings["clientID"] #reddit app client id for praw
clientSecret = settings["clientSecret"] #reddit app client secret for praw
userAgent = settings["agentName"] #reddit app user agent name for praw
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
redSkip = settings["redditSkip"] #skip reddit scrapes?
instaSkip = settings["instaSkip"] #skip insta scrapes?
userList = [] #processed list of reddit users
subList = [] #processed listof subreddits
instaAccounts = [] #processed list of instagram accounts
#stats for logging
captured = 0
warnings=0
errors = 0


#setup user and subreddit lists
processScrapeList(_scrapeList=scrapeList,_userList=userList,_subList=subList, _instaList = instaList, _instaAccountList=instaAccounts)

#praw reddit client setup
reddit = praw.Reddit(client_id=clientID, client_secret=clientSecret, user_agent=userAgent)

#loop through all reddit users to pull content
for username in userList:
     if(redSkip.lower() == "true"):
          break
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
               ydl_opts = {
                    'formate':'best',
                    'outtmpl': userpath+str(subcount)+"-"+user.name+"-"+"%(title)s.%(ext)s",
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

#loop through all subreddits to pull content
#takes advantage of pushshift api
for subname in subList:
     if(redSkip.lower() == "true"):
          break
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
               ydl_opts = {
                    'formate':'best',
                    'outtmpl': subpath+str(subcount)+"-"+subname+"-"+"%(title)s.%(ext)s",
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

#loop through all insta profiles to scrape content
for profile in instaList:
     if  instaSkip.lower() == "true":
          break
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

endTime = datetime.datetime.now()
print("\033[1;32;40mDownloaded:",str(captured),"\nDuration:",datetime.timedelta(seconds=(endTime - startTime).total_seconds()))
if loggingLevel >=2:
     print("Warnings:",str(warnings))
if loggingLevel >=1:
     print("Errors:",str(errors))
print(bcolors.ENDC)
