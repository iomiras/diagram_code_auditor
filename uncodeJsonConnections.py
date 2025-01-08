import json

from pprint import pprint

php_json = './tmp/connections.json'

with open(php_json, 'r') as f:
    content = f.read()

python_list = json.loads(content)
pprint(python_list)