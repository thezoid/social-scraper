# social-scraper [![discord](https://img.shields.io/discord/136001983852052480.svg?label=&logo=discord&logoColor=ffffff&color=7389D8&labelColor=6A7EC2)](https://clan.bravebearstudios.com)  [![Tips](https://img.shields.io/badge/Donate-PayPal-green.svg)](paypal.me/BraveBearStudios)

![Linux](https://github.com/thezoid/social-scraper/actions/workflows/app_linuxBuild.yml/badge.svg?branch=master)
![Mac](https://github.com/thezoid/social-scraper/actions/workflows/app_macBuild.yml/badge.svg?branch=master)
![Windows](https://github.com/thezoid/social-scraper/actions/workflows/app_windowsBuild.yml/badge.svg?branch=master)

A quick python project to allow the downloading of content from specificed social sites.

DISCLAIMER: This project is to be used only for archival purposes.

## Requirements

 Requires instaloader, youtube_dl, and praw. praw erquires additional setup; h/e youtube_dl and instaloader work OOTB.

 [How to register app for praw](https://praw.readthedocs.io/en/latest/getting_started/authentication.html#installed-application)
 [Twitter needs a dev app registered](https://developer.twitter.com)

```python
 pip install instaloader
 pip install youtube_dl
 pip install praw
 pip install wget
 pip install tweepy
```

## How to Use

1. Make sure you have installed all the listed requirements above
2. Customize `settings.json` to include all of your appropriate information. USe the tables below if you are unsure of what values you should use.
3. Run `scraper.py` through your favorite method
     - *NOTE:* It is recommended to run this through the command line to more easily observe any output that may come up

## Customization

Before putting the bot to work, you need to configure `settings.json` so that the script will function correctly. Be sure not to commit or otherwise save your sensitive information in a public place (keys, secrets, etc.).

|Key|Description| Default |
| --- | --- | --- |
|subRedditSkip|Whether to skip processing Subreddits|false|
|redditorSkip|Whether to skip processing Redditors|false|
|instaSkip|Whether to skip processing Instagram|false|
|twitSkip|Whether to skip processing Twitter|false|
|red_agentName*|Your reddit app agent name|*N/A*|
|red_clientID*|Your reddit app client ID|*N/A*|
|red_clientSecret*|Your Reddit app client secret|*N/A*|
|twit_consKey*|Your Twitter developer app consumer API key|*N/A*|
|twit_consSec*|Your Twitter developer app consumer secret|*N/A*|
|twit_bearerTok*|Your Twitter developer app bearer token|*N/A*|
|destination|The location to write scraped content to|*N/A*|
|loggingLevel|Set the level of logging in the script such that <br><ul><li>`0 = SILENT`</li><li>`1 = ERROR`</li><li>`2 = WARNING`</li><li>`3 = INFO`</li></ul>|1|
|imageDomains|A list of allowed GIF domains to download from|`"i.redd.it","i.imgur.com"`|
|gifDomains|A list of allowed GIF domains to download from|`"gfycat.com"`|
|videoDomains|A list of allowed video domains to download from|`"v.redd.it","gfycat.com"`|
|scrapeList|A list of Reddit users or subreddits to scrape media from. **Must** assign as `r/subredditName` or `u/redditorName`|*N/A*|
|instaList|A list of Instagram handles to scrape media from|*N/A*|
|twitterList|A list of Twitter handles to scrape media from|*N/A*|

****If you update these in your settings, please do not commit it to your local repository! I do not take responsibility for any data that may leak through your commits!***

## Known restrictions

- When doing large scrapes from public Instagrams, you will be rate limited to pulling 12 images per profile
     - Instaloader does this as a precaution
     - Support will not be offered for this and developer(s) will not work around it
- Some posts will fail to download due to content no longer existing

## Support

Join my [Discord](https://clan.bravebearstudios.com) and join the Programmer's Parlor. #code-talk can be used to discuss this project, and code in general. Assistance may be provided on a case by case instance; however no offical or 24/7 support will be provided. **Do not** ping mods or admins for assitance for code.