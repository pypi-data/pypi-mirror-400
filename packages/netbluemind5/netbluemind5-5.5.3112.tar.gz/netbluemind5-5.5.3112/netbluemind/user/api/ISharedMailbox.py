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

ISharedMailbox_VERSION = "5.5.3112"


class ISharedMailbox(BaseEndpoint):
    def __init__(self, apiKey, url, domainUid):
        self.url = url
        self.apiKey = apiKey
        self.base = url + '/shared_mailboxes/{domainUid}'
        self.domainUid_ = domainUid
        self.base = self.base.replace('{domainUid}', domainUid)

    def allUids(self):
        postUri = "/_alluids"
        __data__ = None
        __encoded__ = None
        queryParams = {}

        response = requests.get(self.base + postUri, params=queryParams, verify=False, headers={
                                'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': ISharedMailbox_VERSION}, data=__encoded__)
        return self.handleResult__(serder.ListSerDer(serder.STRING), response)

    def byEmail(self, email):
        postUri = "/byEmail/{email}"
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{email}", email)
        queryParams = {}

        response = requests.get(self.base + postUri, params=queryParams, verify=False, headers={
                                'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': ISharedMailbox_VERSION}, data=__encoded__)
        from netbluemind.user.api.SharedMailbox import SharedMailbox
        from netbluemind.user.api.SharedMailbox import __SharedMailboxSerDer__
        from netbluemind.core.container.model.ItemValue import ItemValue
        from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
        return self.handleResult__(__ItemValueSerDer__(__SharedMailboxSerDer__()), response)

    def byName(self, login):
        postUri = "/byName/{login}"
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{login}", login)
        queryParams = {}

        response = requests.get(self.base + postUri, params=queryParams, verify=False, headers={
                                'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': ISharedMailbox_VERSION}, data=__encoded__)
        from netbluemind.user.api.SharedMailbox import SharedMailbox
        from netbluemind.user.api.SharedMailbox import __SharedMailboxSerDer__
        from netbluemind.core.container.model.ItemValue import ItemValue
        from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
        return self.handleResult__(__ItemValueSerDer__(__SharedMailboxSerDer__()), response)

    def delete(self, uid):
        postUri = "/{uid}"
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{uid}", uid)
        queryParams = {}

        response = requests.delete(self.base + postUri, params=queryParams, verify=False, headers={
                                   'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': ISharedMailbox_VERSION}, data=__encoded__)
        from netbluemind.core.task.api.TaskRef import TaskRef
        from netbluemind.core.task.api.TaskRef import __TaskRefSerDer__
        return self.handleResult__(__TaskRefSerDer__(), response)

    def getComplete(self, uid):
        postUri = "/{uid}/complete"
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{uid}", uid)
        queryParams = {}

        response = requests.get(self.base + postUri, params=queryParams, verify=False, headers={
                                'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': ISharedMailbox_VERSION}, data=__encoded__)
        from netbluemind.user.api.SharedMailbox import SharedMailbox
        from netbluemind.user.api.SharedMailbox import __SharedMailboxSerDer__
        from netbluemind.core.container.model.ItemValue import ItemValue
        from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
        return self.handleResult__(__ItemValueSerDer__(__SharedMailboxSerDer__()), response)

    def getLight(self, uid):
        postUri = "/{uid}/light"
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{uid}", uid)
        queryParams = {}

        response = requests.get(self.base + postUri, params=queryParams, verify=False, headers={
                                'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': ISharedMailbox_VERSION}, data=__encoded__)
        from netbluemind.user.api.SharedMailbox import SharedMailbox
        from netbluemind.user.api.SharedMailbox import __SharedMailboxSerDer__
        from netbluemind.core.container.model.ItemValue import ItemValue
        from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
        return self.handleResult__(__ItemValueSerDer__(__SharedMailboxSerDer__()), response)

    def getVCard(self, uid):
        postUri = "/{uid}/vcard"
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{uid}", uid)
        queryParams = {}

        response = requests.get(self.base + postUri, params=queryParams, verify=False, headers={
                                'X-BM-ApiKey': self.apiKey, 'Accept': 'application/json', 'X-BM-ClientVersion': ISharedMailbox_VERSION}, data=__encoded__)
        from netbluemind.addressbook.api.VCard import VCard
        from netbluemind.addressbook.api.VCard import __VCardSerDer__
        return self.handleResult__(__VCardSerDer__(), response)
