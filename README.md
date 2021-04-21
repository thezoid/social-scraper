# social-scraper

A quick python project to allow the downloading of content from specificed social sites.

DISCLAIMER: This project is to be used only for archival purposes.

## requirements

 Requires instaloader, youtube_dl, and praw. praw erquires additional setup; h/e youtube_dl and instaloader work OOTB.

 [How to register app for praw](https://praw.readthedocs.io/en/latest/getting_started/authentication.html#installed-application)


```python
 pip install instaloader
 pip install youtube_dl
 pip install praw
```

## known restrictions

- When doing large scrapes from public Instagrams, you will be rate limited to pulling 12 images per profile
- Some posts will fail to download due to content no longer being present