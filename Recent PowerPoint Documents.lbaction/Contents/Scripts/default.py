#!/usr/bin/env python3

import json, operator
import mruservice, mruuserdata

APP_NAME = 'PowerPoint'
APP_BUNDLE_ID = 'com.microsoft.PowerPoint'
APP_URL_PREFIX = 'ms-powerpoint:ofe|u|'
EXTENSION_TO_ICON_NAME = dict(
    pptx='PPTX', xml='PPTX', thmx='THMX', ppt='SLD8', potx='POTX', pot='PPOT', odp='PODP',
    ppsx='PPSX', pps='PPSS', pptm='PPTM', potm='POTM', ppsm='PPSM', _='TEXT')

items = mruuserdata.items_for_app(APP_NAME)
items += mruservice.items_for_app(APP_NAME, APP_BUNDLE_ID, APP_URL_PREFIX, EXTENSION_TO_ICON_NAME)

items.sort(key=operator.itemgetter('Timestamp'), reverse=True)

print(json.dumps(items))
