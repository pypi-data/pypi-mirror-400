#
#  BEGIN LICENSE
#  Copyright (c) Blue Mind SAS, 2012-2016
#
#  This file is part of BlueMind. BlueMind is a messaging and collaborative
#  solution.
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of either the GNU Affero General Public License as
#  published by the Free Software Foundation (version 3 of the License).
#
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  See LICENSE.txt
#  END LICENSE
#
import requests
import json
from netbluemind.python import serder
from netbluemind.python.client import BaseEndpoint

IMailFinder_VERSION = "5.5.3112"


class IMailFinder(BaseEndpoint):
    def __init__(self, apiKey, url, domainUid):
        self.url = url
        self.apiKey = apiKey
        self.base = url + '/mail_finder/{domainUid}'
        self.domainUid_ = domainUid
        self.base = self.base.replace('{domainUid}', domainUid)

    def search(self, query):
        postUri = "/_search/"
        __data__ = None
        __encoded__ = None
        from netbluemind.backend.mail.api.MailFinderQuery import MailFinderQuery
        from netbluemind.backend.mail.api.MailFinderQuery import __MailFinderQuerySerDer__
        __data__ = __MailFinderQuerySerDer__().encode(query)
        __encoded__ = json.dumps(__data__)
        queryParams = {}

        response = requests.post(self.base + postUri, params=queryParams, verify=False, headers={
                                 'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': IMailFinder_VERSION}, data=__encoded__)
        from netbluemind.backend.mail.api.SearchResult import SearchResult
        from netbluemind.backend.mail.api.SearchResult import __SearchResultSerDer__
        return self.handleResult__(__SearchResultSerDer__(), response)
