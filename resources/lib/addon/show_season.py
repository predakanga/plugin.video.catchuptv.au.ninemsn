#
#   NineMSN CatchUp TV Video Addon
#
#   This code is forked from Network Ten CatchUp TV Video Addon
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

import sys
import pickle
import urllib
import utils
import xbmcgui
import xbmcplugin

from ninemsnvideo.api import NineMSNVideo

class Main:
    def __init__( self, params ):
        self.client = NineMSNVideo()
        handle = int(sys.argv[1])
        show = params['id'][0]
        prefix = params['fullname'][0]
        season = None
        if 'season' in params:
          season = params['season'][0] or None # If season is an empty string, this will replace it with None
        
        def get_url(action, uuid, url):
          url_base = sys.argv[0]
          url_params = {'action': action, 'uuid': uuid, 'page_url': url}
          
          return "{0}?{1}".format(url_base, urllib.urlencode(url_params))
        
        for video in self.client.get_videos_for_season(show, season):
          li = xbmcgui.ListItem("{0} {1}".format(prefix, video.name))
          li.setProperty('IsPlayable', 'true')
          xbmcplugin.addDirectoryItem(handle=handle, listitem=li, url=get_url('play', video.uuid, video.url))

        xbmcplugin.addSortMethod( handle=handle, sortMethod=xbmcplugin.SORT_METHOD_NONE )
        xbmcplugin.setContent( handle=handle, content='tvshows' )
        xbmcplugin.endOfDirectory( handle=handle, succeeded=1 )