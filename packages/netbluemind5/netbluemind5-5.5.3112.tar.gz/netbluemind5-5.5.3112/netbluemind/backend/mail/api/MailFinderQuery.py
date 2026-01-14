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
from netbluemind.python import serder


class MailFinderQuery:
    def __init__(self):
        self.from_ = None
        self.subject = None
        self.messageId = None
        self.before = None
        self.after = None
        pass


class __MailFinderQuerySerDer__:
    def __init__(self):
        pass

    def parse(self, value):
        if (value == None):
            return None
        instance = MailFinderQuery()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        from_Value = value['from']
        instance.from_ = serder.STRING.parse(from_Value)
        subjectValue = value['subject']
        instance.subject = serder.STRING.parse(subjectValue)
        messageIdValue = value['messageId']
        instance.messageId = serder.STRING.parse(messageIdValue)
        beforeValue = value['before']
        instance.before = serder.STRING.parse(beforeValue)
        afterValue = value['after']
        instance.after = serder.STRING.parse(afterValue)
        return instance

    def encode(self, value):
        if (value == None):
            return None
        instance = dict()
        self.encodeInternal(value, instance)
        return instance

    def encodeInternal(self, value, instance):

        from_Value = value.from_
        instance["from"] = serder.STRING.encode(from_Value)
        subjectValue = value.subject
        instance["subject"] = serder.STRING.encode(subjectValue)
        messageIdValue = value.messageId
        instance["messageId"] = serder.STRING.encode(messageIdValue)
        beforeValue = value.before
        instance["before"] = serder.STRING.encode(beforeValue)
        afterValue = value.after
        instance["after"] = serder.STRING.encode(afterValue)
        return instance
