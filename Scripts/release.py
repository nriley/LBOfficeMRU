#!/usr/bin/env python3

import argparse
import compileall
import glob
import json
import os
import plistlib
import shutil
import subprocess
import sys
import tempfile
import webbrowser

from packaging.version import Version
from urllib.parse import quote, urlencode

def update_bundle_version(bundle_path, version, repo):
    info_plist_path = os.path.join(bundle_path, 'Contents', 'Info.plist')
    with open(info_plist_path, 'rb') as plist_file:
        info_plist = plistlib.load(plist_file)

    info_plist['CFBundleVersion'] = version
    info_plist['LBDescription']['LBDownloadURL'] = expand_url_template(
        'https://github.com/%s/releases/download/%s/%s-%s.zip', repo,
        tag_for_version(version), repo.split('/', 1)[1], version)

    with open(info_plist_path, 'wb') as plist_file:
        plistlib.dump(info_plist, plist_file)

def sign_bundle(bundle_path):
    subprocess.check_call(['/usr/bin/codesign', '-fs', 'Developer ID Application: Nicholas Riley',
                           bundle_path])

def output(*args):
    return subprocess.check_output(args, encoding='utf-8')

PROJECT_PATH = None
def project_path():
    global PROJECT_PATH
    if PROJECT_PATH is None:
        PROJECT_PATH = output('/usr/bin/git', '-C', os.path.dirname(__file__),
                             'rev-parse', '--show-toplevel').rstrip('\n')
    return PROJECT_PATH

def git(*args):
    return output('/usr/bin/git', '-C', project_path(), *args)

def archive_bundles(product_name, version, bundle_paths):
    file_paths = git('ls-files', '-z', *bundle_paths).rstrip('\0').split('\0')

    git('commit', '-am', version)

    temp_dir_path = tempfile.mkdtemp(prefix='upload_' + product_name)
    archive_dir_path = os.path.join(temp_dir_path, '%s %s' % (product_name, version), '')
    git('checkout-index', '--prefix=' + archive_dir_path, *file_paths)
    git('reset', 'HEAD~')

    for py_path in (f for f in file_paths if f.endswith('.py')):
        py_path = os.path.join(archive_dir_path, py_path)
        compileall.compile_file(py_path)
        # can't delete default.py because LaunchBar won't let me point at a .pyc
        if os.path.split(py_path)[1] != 'default.py':
            os.unlink(py_path)

    for bundle_path in bundle_paths:
        sign_bundle(os.path.join(archive_dir_path, bundle_path))

    # note: a single action can be zipped into a .lbaction file instead
    archive_path = os.path.join(project_path(), '%s-%s.zip' % (product_name, version))
    subprocess.check_call(['/usr/bin/ditto', '-ck', temp_dir_path, archive_path])
    shutil.rmtree(temp_dir_path)

    return archive_path

def expand_url_template(url_template, *args, **query):
    url = url_template
    if args:
        url = url % tuple(map(quote, args))
    if query:
        url += '?' + urlencode(query)
    return url

def tag_for_version(version):
    return 'v' + version

def upload_release(repo, version, archive_path, github_access_token):
    package_version = Version(version)

    releases_url = expand_url_template(
        'https://api.github.com/repos/%s/releases', repo)

    release_name = tag_for_version(version)
    release_json = dict(tag_name=release_name, target_commitish='master',
                        name=release_name, body='', draft=True,
                        prerelease=package_version.is_prerelease)

    print(releases_url)

    releases_api = subprocess.Popen(
        ['/usr/bin/curl', '-u', 'nriley:' + github_access_token,
         '--data', '@-', releases_url],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, encoding='utf-8')
    release_json_data, _ = releases_api.communicate(json.dumps(release_json))
    release_json = json.loads(release_json_data)

    html_url = release_json['html_url']
    upload_url = release_json['upload_url'].split('{', 1)[0]
    upload_url = expand_url_template(upload_url,
        name=os.path.basename(archive_path), access_token=github_access_token)
    subprocess.check_call(
        ['/usr/bin/curl', '-H', 'Content-Type: application/zip',
         '--data-binary', '@' + archive_path, upload_url])

    return html_url

def release(version, github_access_token):
    repo = 'nriley/LBOfficeMRU'
    os.chdir(project_path())
    action_paths = glob.glob('*.lbaction')

    for action_path in action_paths:
        # update version number and download URL in the working copy so it can be committed
        update_bundle_version(action_path, version, repo)

    archive_path = archive_bundles('LBOfficeMRU', version, action_paths)

    if github_access_token is None:
        return

    html_url = upload_release('nriley/LBOfficeMRU', version, archive_path, github_access_token)
    webbrowser.open(html_url)

    print("Make sure changes are committed and pushed before saving release as final!")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Build and optionally release to GitHub.')
    parser.add_argument('version')
    parser.add_argument('github_access_token', nargs='?', default=None)

    args = parser.parse_args()

    release(args.version, args.github_access_token)
