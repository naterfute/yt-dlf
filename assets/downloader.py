import os
import yt_dlp
from munch import munchify
from typing import Optional
from json import JSONEncoder
if __name__ == 'downloader':
  from db import database
else:
  pass

class MyLogger:
    def debug(self, msg):
        # For compatibility with youtube-dl, both debug and info are passed into debug
        # You can distinguish them by the prefix '[debug] '
        if msg.startswith('[debug] '):
            pass
        else:
            self.info(msg)

    def info(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)


class Downloader:
  Started=False
  web_use=False
  server=False
  host=''
  port=''
  download_path=''
  Status=''
  filename=''
  time_elapse=''
  percent=''
  eta=''
  url=''
  title=''

  def __init__(
    self, host:Optional[str]=None, 
    download_path:Optional[str]='downloads/', 
    port:Optional[int]=5000,
    server:Optional[bool]=False
  ):
    if not host == None:
      self.web_use = True
      self.host = host
      self.port = port
      self.download_path = download_path
    elif server:
      self.server=True
    else:
      pass
    
  
  def progress_hook(self, d):    
    if d['status'] == 'finished':
      print(f'Done Downloading "{d['filename']}"')
      self.Started = False
      self.filename = d['filename']
      self.time_elapse = d['elapsed']
      # print(d['_elapsed_str'])
      # print(d['elapsed'])
    if d['status'] == 'downloading':
      if self.Started:
        print(d['_percent_str'], d['_eta_str'])
        
      else: 
        print(f'Now Downloading "{d['tmpfilename']}"')
        self.filename = d['tmpfilename']
        self.percent = d['_percent_str']
        self.eta = d['_eta_str']
        print(d['_percent_str'], d['_eta_str'])
        self.Started = True
        
  def postprocessor_hooks(self, d):
    if d['status'] == 'started':
      info = munchify(d['info_dict'])
      self.url = info.webpage_url
      self.title = info.title
      self.download_path = info.filepath
      self.Status = 'Started'
      pass
    if d['status'] == 'finished':
      self.Status = 'Finished'
      pass

  def ydl_opts(self):
    ydl_opts = {
      # 'ratelimit': 500, # Kilobytes
      'logger': MyLogger(),
      'breakonexisting': True,
      'progress_hooks': [self.progress_hook],
      'postprocessor_hooks': [self.postprocessor_hooks],
      'format': 'bestaudio/best',
      'writethumbnail': True,
      'outtmpl': 'downloads/%(playlist_title)s/%(title)s.%(ext)s',
      'postprocessors': [
      {'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': 'None'},
      {'add_metadata': 'True', 'key': 'FFmpegMetadata'},
      {'already_have_thumbnail': False, 'key': 'EmbedThumbnail'}
    ]}
    return ydl_opts

    
  def download(self, urls):
    if not self.server:
      for x in urls:
        with yt_dlp.YoutubeDL(self.ydl_opts()) as ydl:
          ydl.download(x)
    else:    
      with yt_dlp.YoutubeDL(self.ydl_opts()) as ydl:
        ydl.download(urls)
        db = database()
        db.write_to_db(self.title, self.url, self.download_path, self.time_elapse)


  def json(self):
    data = {
      'WebUse': {
        'use': self.web_use,
        'host': self.host,
        'port': self.port
        },
      'Started': self.Started,
      'info': {
      'Download_path': self.download_path,
      'filename': self.filename,
      'time_elapse': self.time_elapse,
      'percent': self.percent,
      'eta': self.eta
      },
    }
    return data
