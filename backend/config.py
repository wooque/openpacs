import os

import yaml
from yaml.loader import FullLoader

default_config = {
    'secret': 'default',
    'superadmin_pass': 'pa55w0rd',
    'db_host': '127.0.0.1',
    'db_database': 'openpacs',
    'db_user': 'openpacs',
    'db_password': 'pa55w0rd',
    'es_host': 'localhost',
}

config = default_config.copy()
try:
    local_file = open('config.local.yaml').read()
    local_config = yaml.load(local_file, Loader=FullLoader)
    for k, v in config.items():
        if k in local_config:
            config[k] = local_config[k]
except:
    pass

for k in default_config.keys():
    kenv = k.upper()
    env_val = os.getenv(kenv)
    if env_val:
        config[k] = env_val

if config['secret'] == 'default':
    config['secret'] = config['db_password']

is_docker = bool(os.getenv('OPENPACS_DOCKER'))
