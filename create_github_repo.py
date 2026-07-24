import json
import os
import sys
from urllib import request, error

if len(sys.argv) != 3:
    print('Usage: python create_github_repo.py <github_username> <repo_name>')
    sys.exit(1)

username = sys.argv[1]
repo_name = sys.argv[2]

token = os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')
if not token:
    print('Error: GH_TOKEN or GITHUB_TOKEN environment variable not set.')
    sys.exit(1)

headers = {
    'Authorization': 'token ' + token,
    'Accept': 'application/vnd.github.v3+json',
    'User-Agent': 'python-urllib'
}

url = f'https://api.github.com/repos/{username}/{repo_name}'
req = request.Request(url, headers=headers, method='GET')
try:
    with request.urlopen(req) as resp:
        print(f'Repository {username}/{repo_name} already exists.')
        sys.exit(0)
except error.HTTPError as e:
    if e.code != 404:
        print(f'Failed to check repository existence: {e.code} {e.reason}')
        print(e.read().decode('utf-8'))
        sys.exit(1)

create_url = 'https://api.github.com/user/repos'
body = json.dumps({
    'name': repo_name,
    'private': False,
    'description': 'gfast-ui project upload'
}).encode('utf-8')
create_req = request.Request(create_url, data=body, headers=headers, method='POST')
try:
    with request.urlopen(create_req) as resp:
        data = json.load(resp)
        print('Created repository:', data.get('full_name'))
        print('Clone URL:', data.get('clone_url'))
except error.HTTPError as e:
    print(f'Failed to create repository: {e.code} {e.reason}')
    print(e.read().decode('utf-8'))
    sys.exit(1)
