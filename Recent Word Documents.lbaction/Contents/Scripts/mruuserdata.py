from urlparse import urlsplit
import os, sqlite3

__all__ = ('items_for_app',)

SQL = """select url.value URL, ts.value Timestamp from HKEY_CURRENT_USER_values url
join HKEY_CURRENT_USER_values ts using (node_id)
join HKEY_CURRENT_USER_values filename using (node_id)
join HKEY_CURRENT_USER uuid using (node_id)
join HKEY_CURRENT_USER documents on uuid.parent_id = documents.node_id and documents.name = 'Documents'
join HKEY_CURRENT_USER local on documents.parent_id = local.node_id and local.name = 'Local'
join HKEY_CURRENT_USER app on local.parent_id = app.node_id and app.name = ?
join HKEY_CURRENT_USER user on app.parent_id = user.node_id
join HKEY_CURRENT_USER mru on user.parent_id = mru.node_id and mru.name = 'MruUserData'
join HKEY_CURRENT_USER common on mru.parent_id = common.node_id and common.name = 'Common'
join HKEY_CURRENT_USER version on common.parent_id = version.node_id
join HKEY_CURRENT_USER office on version.parent_id = office.node_id and office.name = 'Office'
join HKEY_CURRENT_USER microsoft on office.parent_id = microsoft.node_id and microsoft.name = 'Microsoft'
join HKEY_CURRENT_USER software on microsoft.parent_id = software.node_id and software.name = 'Software'
where software.parent_id = -1
and url.name = 'DocumentUrl' and ts.name = 'Timestamp' and filename.name = 'FileName'
order by ts.value desc
"""

def items_for_app(app_name):
    conn = sqlite3.connect(os.path.expanduser(
        '~/Library/Group Containers/UBF8T346G9.Office/MicrosoftRegistrationDB.reg'))

    items = []

    for url, timestamp in conn.execute(SQL, (app_name,)):
    	# urlsplit should not ordinarily raise
    	# if it does, let it through so the user knows and can report an issue
    	items.append(dict(path=urlsplit(url).path, Timestamp=timestamp))

    return items
