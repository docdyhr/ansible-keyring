#!/usr/bin/env python3

import keyring

LABEL = "banna"
ACCOUNT_NAME = "monkeybiz"

PASSWD = keyring.get_password(LABEL, ACCOUNT_NAME)

print(PASSWD)
