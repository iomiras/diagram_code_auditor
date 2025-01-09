import os
import subprocess, json

php_parser = 'utils/php_parser.php'
php_connection_parser = 'utils/connection_parser.php'

php_data_file = 'utils/tmp/data.json'
php_connections_file = 'utils/tmp/connections.json'

def extract_php_data(file_path):
    """
    Parse and analyze a PHP code file's content.

    Args:
        file_path: File path to the PHP code file.

    Returns:
        tuple: (classes, methods, attributes)
    """
    global php_parser, php_data_file
    subprocess.run(['php', php_parser, file_path, php_data_file])

    with open(php_data_file, 'r') as f:
        content = f.read()
    parsed_json_list = json.loads(content)
    return parsed_json_list['classes'], parsed_json_list['classToMethods'], parsed_json_list['classToAttributes']

def extract_connections(file_path):
    global php_connection_parser, php_connections_file, php_data_file

    _php_data_file = php_data_file.split('/')[-1].split('.')[0] + '_temp.json'

    subprocess.run(['php', php_connection_parser, file_path, _php_data_file, php_connections_file])

    os.remove(_php_data_file)
    with open(php_connections_file, 'r') as f:
        content = f.read()

    return json.loads(content)