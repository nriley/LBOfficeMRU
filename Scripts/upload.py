#!/usr/bin/python

import argparse
import distutils.version
import glob
import json
import os
import plistlib
import shutil
import subprocess
import sys
import tempfile
import urllib
import webbrowser

def update_bundle_version(bundle_path, version):
    info_plist_path = os.path.join(bundle_path, 'Contents', 'Info.plist')
    info_plist = plistlib.readPlist(info_plist_path)
    info_plist['CFBundleVersion'] = version
    plistlib.writePlist(info_plist, info_plist_path)

def sign_bundle(bundle_path):
    subprocess.check_call(['/usr/bin/codesign', '-fs', 'Developer ID Application: Nicholas Riley',
                           bundle_path])

def archive_items(product_name, version, dir_path, items):
    temp_dir_path = tempfile.mkdtemp(prefix='upload_' + product_name)
    subprocess.check_call(['/bin/cp', '-Rp'] + items + [temp_dir_path])

    # note: a single action can be zipped into a .lbaction file instead
    archive_path = os.path.join(dir_path, '%s-%s.zip' % (product_name, version))
    subprocess.check_call(['/usr/bin/ditto', '-ck', temp_dir_path, archive_path])
    shutil.rmtree(temp_dir_path)

    return archive_path

def expand_url_template(url_template, query=None, *args):
    url = url_template
    if args:
        url = url % tuple(map(urllib.quote, args))
    if query:
        url += '?' + urllib.urlencode(query)
    return url

def upload_release(repo, version, archive_path, github_access_token):
    strict_version = distutils.version.StrictVersion(version)

    releases_url = expand_url_template('https://api.github.com/repos/%s/releases',
                                       dict(access_token=github_access_token), repo)

    release_name = 'v' + version
    release_json = dict(tag_name=release_name, target_commitish='master',
                        name=release_name, body='', draft=True,
                        prerelease=bool(strict_version.prerelease))

    print releases_url

    releases_api = subprocess.Popen(['/usr/bin/curl', '--data', '@-', releases_url],
                                    stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    release_json_data, _ = releases_api.communicate(json.dumps(release_json))
    release_json = json.loads(release_json_data)

    html_url = release_json['html_url']
    upload_url = release_json['upload_url'].split('{', 1)[0]
    upload_url = expand_url_template(upload_url, dict(name=os.path.basename(archive_path),
                                                      access_token=github_access_token))
    subprocess.check_call(['/usr/bin/curl', '-H', 'Content-Type: application/zip',
                           '--data-binary', '@' + archive_path, upload_url])

    return html_url

def release(version, github_access_token):
    project_path = os.path.join(os.path.dirname(__file__), '..')
    action_paths = glob.glob(os.path.join(project_path, '*.lbaction'))

    for action_path in action_paths:
        update_bundle_version(action_path, version)
        sign_bundle(action_path)

    archive_path = archive_items('LBOfficeMRU', version, project_path, action_paths)
    html_url = upload_release('nriley/LBOfficeMRU', version, archive_path, github_access_token)

    webbrowser.open(html_url)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Release to GitHub.')
    parser.add_argument('version')
    parser.add_argument('github_access_token')

    args = parser.parse_args()

    release(args.version, args.github_access_token)
