import os
from urllib.parse import urljoin

import _common

def db_path(key, runtime):
    key_hash = _common.md5(key)
    return os.path.join(runtime.config_data['output_path'], 'db', key_hash[:2], key_hash[2:4], key_hash)

def db_url(key, runtime):
    key_hash = _common.md5(key)
    return _common.urljoin(runtime.config_data['base_url'], 'db', key_hash[:2], key_hash[2:4], key_hash)
