#!/usr/bin/env python

import json, operator
import mruservice

APP_NAME = 'OneNote'
APP_BUNDLE_ID = 'com.microsoft.onenote.mac'
APP_URL_PREFIX = 'onenote:'

items = mruservice.items_for_app(APP_NAME, APP_BUNDLE_ID, APP_URL_PREFIX)

items.sort(key=operator.itemgetter('Timestamp'), reverse=True)

print json.dumps(items)
