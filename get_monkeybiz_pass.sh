/bin/bash

# Keychain query fields.
# LABEL is the value you put for "Keychain Item Name" in Keychain.app.
LABEL="banna"
ACCOUNT_NAME="monkeybiz"

/usr/bin/security find-generic-password -w -a "$ACCOUNT_NAME" -l "$LABEL"