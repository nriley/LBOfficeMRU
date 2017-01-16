#!/usr/bin/env python

import json, operator, os, sqlite3, urllib

APP_NAME = 'OneNote'
APP_BUNDLE_ID = 'com.microsoft.onenote.mac'
APP_SCHEMA = 'onenote'

mruservicecache_path = os.path.expanduser(
    '~/Library/Containers/%s/Data/Library/Application Support/Microsoft/AppData/Office/15.0/MruServiceCache'
    % APP_BUNDLE_ID)


documents = []

for cache_path in os.listdir(mruservicecache_path):
    # XXX localization?
    documents_path = os.path.join(mruservicecache_path, cache_path, APP_NAME, 'Documents_en-US')
    if not os.path.isfile(documents_path):
        continue

    # XXX exception handling
    documents += json.load(file(documents_path))

items = []
seen_urls = set()

documents.sort(key=operator.itemgetter('Timestamp'), reverse=True)

for document in documents:
    url = document['DocumentUrl']
    if url in seen_urls:
        continue
    seen_urls.add(url)
    items.append(dict(title=document['FileName'],
                      subtitle=document['Path'],
                      url='%s:%s' % (APP_SCHEMA,
                                     urllib.quote(document['DocumentUrl'], safe=':/')),
                      icon=APP_BUNDLE_ID))

print json.dumps(items)
