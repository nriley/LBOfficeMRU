import json, os, sys
from urllib.parse import quote

__all__ = ('items_for_app',)

def items_for_app(app_name, app_bundle_id, app_url_prefix, extension_to_icon_name=None):
    mruservicecache_paths = (os.path.expanduser(path) % app_bundle_id for path in (
        '~/Library/Containers/%s/Data/Library/Application Support/Microsoft/Office/16.0/MruServiceCache',
        '~/Library/Containers/%s/Data/Library/Application Support/Microsoft/AppData/Office/15.0/MruServiceCache'))

    for mruservicecache_path in mruservicecache_paths:
        if os.path.isdir(mruservicecache_path):
            break
    else:
        return []

    documents = []

    for cache_path in os.listdir(mruservicecache_path):
        app_path = os.path.join(mruservicecache_path, cache_path, app_name)
        if not os.path.isdir(app_path):
            continue

        for documents_filename in (f for f in os.listdir(app_path) if f.startswith('Documents_')):
            documents_path = os.path.join(app_path, documents_filename)

            if not os.path.isfile(documents_path):
                continue

            try:
                documents += json.load(open(documents_path))
            except ValueError as e:
                print("Can't parse documents MRU cache:", e, file=sys.stderr)
                continue

    items = []
    seen_urls = set()

    for document in documents:
        url = document['DocumentUrl']
        if url in seen_urls:
            continue

        seen_urls.add(url)
        filename = document['FileName']
        if extension_to_icon_name:
            filename, extension = os.path.splitext(filename)
            icon = None
            if extension: icon = extension_to_icon_name.get(extension.lower()[1:])
            if icon is None: icon = extension_to_icon_name['_']
            icon = '%s:%s' % (app_bundle_id, icon)
        else:
            icon = app_bundle_id

        items.append(dict(title=filename,
                          subtitle=document['Path'],
                          url='%s%s' % (app_url_prefix,
                                        quote(document['DocumentUrl'].encode('utf-8'), safe=':/')),
                          icon=app_bundle_id,
                          Timestamp=document['Timestamp']))

    return items
