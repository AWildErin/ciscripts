# AWE_FILE_BEGIN - Erin
# Some useful utilities for build graph options

import os

def get_envvar_str(key: str, default_value: bool) -> str:
    val = os.getenv(key, str(bool)).lower()

    if val in ['true', '1']:
        return 'true'
    else:
        return 'false'
    
def get_envvar_bool(key: str, default_value: bool) -> bool:
    val = os.getenv(key, str(bool)).lower()
    return val in ['true', '1']