#
#   NineMSN CatchUp TV Video API Library
#
#   This code is forked from Network Ten CatchUp TV Video API Library
#   Copyright (c) 2013 Adam Malcontenti-Wilson
# 
#   Permission is hereby granted, free of charge, to any person obtaining a copy
#   of this software and associated documentation files (the "Software"), to deal
#   in the Software without restriction, including without limitation the rights
#   to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#   copies of the Software, and to permit persons to whom the Software is
#   furnished to do so, subject to the following conditions:
# 
#   The above copyright notice and this permission notice shall be included in
#   all copies or substantial portions of the Software.
# 
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#   OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#   THE SOFTWARE.
#

# Try importing default modules, but if that doesn't work
# we might be old platforms with bundled deps
try:
  from BeautifulSoup import BeautifulStoneSoup
except ImportError:
  from deps.BeautifulSoup import BeautifulStoneSoup

try:
  import simplejson as json
except ImportError:
  try:
    import deps.simplejson as json
  except ImportError:
    import json

import os
import sys
import re
import urlparse
import urllib
from brightcove.core import get_item
from utils import log
from collections import namedtuple
from ninemsnvideo.amf import BrightCoveAMFHelper
from ninemsnvideo.cache import Cache
from ninemsnvideo.objects import MediaRenditionItemCollection
import xbmcgui

PLAYER_KEY = 'AQ~~,AAABecFwRRk~,e1HkYhZIbpi8Y_jGTqADve72WwmAmY3L'
AMF_SEED = '8d01b9206a58ca9c4de1015b96b722a2ce91c1df'
SWF_URL = 'http://admin.brightcove.com/viewer/us20130702.1553/connection/ExternalConnection_2.swf'
PAGE_URL = 'http://catchup.ninemsn.com.au/'
CATALOGUE_URL = PAGE_URL + "catalogue"
SECTION_URL = PAGE_URL + "catalogue.aspx?type={0}&page_num={1}&pgfr=1&pgto=10"
SERIES_URL = PAGE_URL + "{0}"
SHOW_REGEX = re.compile('<a href="/([^"]+)">.*?<div class="showinfo">.*?<span class="title">(.*?)</span>.*?<span class="season">Season (.*?)</span>.*?<span class="episode">(\d+) episodes', re.S)
SEASON_REGEX = re.compile('<a href="(/section.aspx\?[^"]+?)">(.*?)</a>')
VIDEO_REGEX = re.compile('<div id\s*=\s*"episode_number"[^>]*uuid="([^"]+)".*?>.*?<h3[^>]*class="season_title".*?>(.*?)</h3>.*?<a id="watch_now[^>]*href="([^"]+)"', re.S)
SECTION_VIDEO_REGEX = re.compile('<img class="videoimage" src="([^"]*)".*?<a class="title">(.*?)</a>.*?<span class="season">(.*?)</span>.*?<span class="episode">(.*?)</span>.*?<a href="([^"]+)"', re.S)
UUID_REGEX = re.compile('var uuid = "([^"]+)"', re.S)

Section = namedtuple('Section', ['id', 'name'])
Category = namedtuple('Category', ['id', 'name'])
Show = namedtuple('Show', ['id', 'name', 'seasons', 'episode_count'])
Season = namedtuple('Season', ['id', 'name', 'url'])
Video = namedtuple('Video', ['uuid', 'name', 'url'])
SectionVideo = namedtuple('SectionVideo', ['show', 'season', 'name', 'url', 'image'])

if hasattr(sys.modules["__main__"], "cache"):
  cache = sys.modules["__main__"].cache
else:
  cache = Cache("ninemsnvideo", 24)

class NineMSNVideo:
  def _request(self, url, data=None):
    '''Returns a response for the given url and data.'''
    conn = urllib.urlopen(url, data)
    resp = conn.read()
    conn.close()
    return resp
  
  def dialog(self, *args):
    d = xbmcgui.Dialog()
    d.ok(*args)
  
  def make_url_absolute(self, url):
    # Very naive implementation for now
    if not url.startswith('http'):
      return PAGE_URL + url.lstrip('/')
    return url
  
  def get_sections(self):
    return [
      Section('mostrecent',  'Newest'),
      Section('expiring',    'Last Chance'),
      Section('mostpopular', 'Recommended')
    ]
  
  def get_categories(self):
    return [
      Category('all',         'All'),
      Category('action',      'Action'),
      Category('comedy',      'Comedy'),
      Category('documentary', 'Documentary'),
      Category('drama',       'Drama'),
      Category('kids',        'Kids'),
      Category('reality',     'Reality'),
      Category('sport',       'Sport'),
      Category('talkshow',    'Talk Show'),
      Category('thriller',    'Thriller'),
      Category('travel',      'Travel'),
    ]
  
  def get_shows_for_category(self, genre):
    url = CATALOGUE_URL
    if genre != "all":
      url = url + "/" + genre
    
    html = cache.cacheFunction(self._request, url)
    for id, name, seasons, episode_count in SHOW_REGEX.findall(html):
      yield Show(id, name, seasons.split(','), int(episode_count))
  
  def get_seasons_for_show(self, show):
    url = SERIES_URL.format(show)
    
    html = cache.cacheFunction(self._request, url)
    seen = []
    for season_url, name in SEASON_REGEX.findall(html):
      params = urlparse.parse_qs(season_url)
      season_id = params['subsectionname'][0]
      if season_id in seen:
        break
      seen.append(season_id)
      
      yield Season(season_id, name, self.make_url_absolute(season_url))
  
  def get_videos_for_season(self, show, season=None):
    # Start by looking up the season URL
    # TODO: Improve this by adding in-memory cache to cache.py
    url = None
    if not season:
      url = SERIES_URL.format(show)
    else:
      for check_season in self.get_seasons_for_show(show):
        if check_season.id == season:
          url = check_season.url
          break
    # TODO: How best to raise an error?
    if not url:
      raise Exception("Couldn't find season {0} for show {1}".format(season, show))
    
    # Fetch the season page
    html = cache.cacheFunction(self._request, url)
    # And extract the videos
    for uuid, name, url in VIDEO_REGEX.findall(html):
      yield Video(uuid, name, self.make_url_absolute(url))

  def get_videos_for_section(self, section, page=1):
    url = SECTION_URL.format(section, page)
    html = cache.cacheFunction(self._request, url)
    
    for img, show, season, episode, url in SECTION_VIDEO_REGEX.findall(html):
      yield SectionVideo(show, season, episode, self.make_url_absolute(url), img)

  def get_uuid_from_url(self, url):
    html = cache.cacheFunction(self._request, url)
    match = UUID_REGEX.search(html)
    if not match:
      self.dialog("Playback Error", "{0} does not appear to contain a NineMSN video".format(url))
    return match.group(1)

  def get_media_for_video(self, videoId=None, video=None):
    # Note to self: Although we *can* access the video content via the Media API
    # (docs: http://support.brightcove.com/en/video-cloud/docs/accessing-video-content-media-api)
    # and it's much easier/flexible, we aren't so as not to arouse suspicion and to future proof the library
    #self.brightcove.find_video_by_id(video.id, fields='length,renditions,FLVURL')
    if video:
      videoId = video.id
    amfHelper = BrightCoveAMFHelper(PLAYER_KEY, videoId, PAGE_URL, AMF_SEED)
    log("{0}".format(amfHelper.data['renditions']))
    return get_item({'items':amfHelper.data['renditions']}, MediaRenditionItemCollection)
