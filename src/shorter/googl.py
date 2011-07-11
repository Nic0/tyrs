# -*- coding: utf-8 -*-
# Copyright © 2011 Nicolas Paris <nicolas.caen@gmail.com>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import httplib2
from urlshorter import UrlShorter

from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import AccessTokenRefreshError
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.tools import run

FLOW = OAuth2WebServerFlow(
    client_id='382344260739.apps.googleusercontent.com',
    client_secret='fJwAFxKWyW4rBmzzm6V3TVsZ',
    scope='https://www.googleapis.com/auth/urlshortener',
    user_agent='urlshortener-tyrs/1.0')

class GooglUrlShorter(UrlShorter):

    def do_shorter(self, longurl):

        home = os.environ['HOME']
        storage = Storage(home + '/.config/tyrs/googl.tok')
        credentials = storage.get()
        if credentials is None or credentials.invalid:
            credentials = run(FLOW, storage)

        http = httplib2.Http()
        http = credentials.authorize(http)

        service = build("urlshortener", "v1", http=http)

        try:

            url = service.url()

            body = {"longUrl": longurl }
            resp = url.insert(body=body).execute()

            return resp['id']

        except AccessTokenRefreshError:
            pass
