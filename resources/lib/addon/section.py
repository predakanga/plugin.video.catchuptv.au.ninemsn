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
        section = params['id'][0]
        page = 1
        if 'page' in params:
          page = int(params['page'][0])
        
        def get_play_url(url):
          url_base = sys.argv[0]
          url_params = {'action': 'play', 'page_url': url}
          
          return "{0}?{1}".format(url_base, urllib.urlencode(url_params))
        
        def get_page_url(page):
          url_base = sys.argv[0]
          url_params = {'action': 'section', 'id': section, 'page': page}
          
          return "{0}?{1}".format(url_base, urllib.urlencode(url_params))
        
        for video in self.client.get_videos_for_section(section, page):
          li = xbmcgui.ListItem("{0} - {1}".format(video.show, video.name), thumbnailImage=video.image)
          li.setProperty('IsPlayable', 'true')
          # Set the image if we have one
          xbmcplugin.addDirectoryItem(handle=handle, listitem=li, url=get_play_url(video.url))

        # And tack on the "Next page" option all the time; should really check if there *is* a next page first
        # Instead, let's just clamp it to 10 pages
        if section != 'mostpopular' and page != 10:
          li = xbmcgui.ListItem("Next Page")
          xbmcplugin.addDirectoryItem(handle=handle, listitem=li, url=get_page_url(page+1), isFolder=True)
        
        xbmcplugin.addSortMethod( handle=handle, sortMethod=xbmcplugin.SORT_METHOD_NONE )
        xbmcplugin.setContent( handle=handle, content='tvshows' )
        xbmcplugin.endOfDirectory( handle=handle, succeeded=1 )