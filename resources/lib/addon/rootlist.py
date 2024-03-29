#
#   Network Ten CatchUp TV Video Addon
#
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
        
        def get_url(action, id):
          url_base = sys.argv[0]
          url_params = {'action': action, 'id': id}
          
          return "{0}?{1}".format(url_base, urllib.urlencode(url_params))
        
        for section in self.client.get_sections():
          li = xbmcgui.ListItem(section.name)
          xbmcplugin.addDirectoryItem(handle=handle, listitem=li, url=get_url('section', section.id), isFolder=True)
        
        for category in self.client.get_categories():
          li = xbmcgui.ListItem(category.name)
          xbmcplugin.addDirectoryItem(handle=handle, listitem=li, url=get_url('category', category.id), isFolder=True)

        # xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE ) # Needed?
        xbmcplugin.setContent( handle=handle, content='tvshows' )
        xbmcplugin.endOfDirectory( handle=handle, succeeded=1 )