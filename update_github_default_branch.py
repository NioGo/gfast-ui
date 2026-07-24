import json
import os
import sys
from urllib import request, error

if len(sys.argv) != 3:
    print('Usage: python update_github_default_branch.py <github_username> <repo_name>')
    sys.exit(1)

username = sys.argv[1]
repo_name = sys.argv[2]

token = os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN') or os.environ.get('TOKEN')
if not token:
    print('Error: GH_TOKEN, GITHUB_TOKEN, or TOKEN environment variable not set.')
    sys.exit(1)

headers = {
    'Authorization': 'token ' + token,
    'Accept': 'application/vnd.github.v3+json',
    'User-Agent': 'python-urllib'
}

# set default branch
url = f'https://api.github.com/repos/{username}/{repo_name}'
data = json.dumps({'default_branch': 'main'}).encode('utf-8')
req = request.Request(url, data=data, headers=headers, method='PATCH')
try:
    with request.urlopen(req) as resp:
        data_resp = json.load(resp)
        print('default branch set to', data_resp.get('default_branch'))
except error.HTTPError as e:
    print('Failed to set default branch:', e.code, e.reason)
    print(e.read().decode('utf-8'))
    sys.exit(1)

# delete old branch
url = f'https://api.github.com/repos/{username}/{repo_name}/git/refs/heads/os-v3.2'
req = request.Request(url, headers=headers, method='DELETE')
try:
    with request.urlopen(req) as resp:
        print('deleted remote branch os-v3.2')
except error.HTTPError as e:
    if e.code == 422:
        print('Branch os-v3.2 already deleted or not found.')
    else:
        print('Failed to delete branch os-v3.2:', e.code, e.reason)
        print(e.read().decode('utf-8'))
        sys.exit(1)
