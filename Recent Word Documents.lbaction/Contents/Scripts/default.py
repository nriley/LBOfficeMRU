#!/usr/bin/env python

import json, operator
import mruservice, mruuserdata

APP_NAME = 'Word'
APP_BUNDLE_ID = 'com.microsoft.Word'
APP_URL_PREFIX = 'ms-word:ofe|u|'
EXTENSION_TO_ICON_NAME = dict(
    docx='WXBN', doc='W8BN', dotx='WXTN', dot='W8TN', docm='WXBM', dotm='WXTM',
    xml='WXML', mht='WDZ9', mhtm='WDZ9', mhtml='WDZ9', odt='ODT', _='TEXT')

items = mruuserdata.items_for_app(APP_NAME)
items += mruservice.items_for_app(APP_NAME, APP_BUNDLE_ID, APP_URL_PREFIX, EXTENSION_TO_ICON_NAME)

items.sort(key=operator.itemgetter('Timestamp'), reverse=True)

print json.dumps(items)
