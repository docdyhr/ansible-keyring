#!/usr/bin/env python3


import sys
import getpass
import keyring

from ansible.config.manager import ConfigManager, get_ini_config_value

config = ConfigManager()

username = get_ini_config_value(
    config._parsers[config._config_file],
    dict(section='vault', key='username')
) or getpass.getuser()

keyname = get_ini_config_value(
    config._parsers[config._config_file],
    dict(section='vault', key='keyname')
) or 'ansible'

print('username: %s keyname: %s' % (username, keyname))
