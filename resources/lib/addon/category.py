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
        category = params['id'][0]
        
        def get_url(action, id, fullname, season=None):
          url_base = sys.argv[0]
          url_params = {'action': action, 'id': id, 'fullname': fullname}
          if season is not None:
            url_params['season'] = season
          
          return "{0}?{1}".format(url_base, urllib.urlencode(url_params))
        
        for show in self.client.get_shows_for_category(category):
          li = xbmcgui.ListItem("{0} ({1} episodes)".format(show.name, show.episode_count))
          if len(show.seasons) > 1:
            url = get_url('show', show.id, show.name)
          else:
            url = get_url('show_season', show.id, show.name, '')
          xbmcplugin.addDirectoryItem(handle=handle, listitem=li, url=url, isFolder=True)

        xbmcplugin.addSortMethod( handle=handle, sortMethod=xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE )
        xbmcplugin.setContent( handle=handle, content='tvshows' )
        xbmcplugin.endOfDirectory( handle=handle, succeeded=1 )