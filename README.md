# ansible-keyring

Access ansible passwords securely with keyring from Mac keychain.

## prerequisites

[python](https://www.python.org)  
[ansible](https://www.ansible.com)  
[keyring](https://pypi.org/project/keyring/)

Install keyring with pip in your terminal

```cli
python3 -m pip install keyring
```

```cli
keyring set [system] [username]
```

Add ansible password and check that it works.

```cli
keyring get [system] [username]
```

## Install [community.general.keyring](https://docs.ansible.com/ansible/latest/collections/community/general/keyring_lookup.html#ansible-collections-community-general-keyring-lookup)

The keyring plugin allows you to access data stored in the OS provided keyring/keychain. The keyring plugin is part of the Community General Collection. To use it you need to install [community.general](https://galaxy.ansible.com/community/general?extIdCarryOver=true&sc_cid=701f2000001OH7YAAW).

Collection Path. By default the community collection is installed in ***~/.ansible/collections/*** folder on macOS.

Check install path:

```cli
ansible-config dump | grep COLLECTIONS_PATHS
```

Costum Path:

```cli
ansible-galaxy collection install community.general -p [Your_Costum_Path]
```

Install from terminal:

```cli
ansible-galaxy collection install community.general
```

Verify your community.general installation:

```cli
ansible-galaxy collection verify community.general -vvv
```

NB! community.general can also be installed as part of requirements.txt in local .env folder.

community.general can be accessed in a yaml files like this:

```yaml
collections:
    - community.general
```

Check keyring doc's

```cli
ansible-doc -t lookup keyring
```

community.general.keyring examples:

```yaml
- name : output secrets to screen (BAD IDEA)
  ansible.builtin.debug:
    msg: "Password: {{item}}"
  with_community.general.keyring:
    - 'servicename username'
```

```yaml
ansible_become_pass=={{ lookup('community.general.keyring','test test') }}
```

### Ressources

[Docs Community.General](https://docs.ansible.com/ansible/latest/collections/community/general/)

### Problems

***TASK [test of keyring plugin]
fatal: [localhost]: FAILED! => {"msg": "Can't LOOKUP(keyring): missing required python library 'keyring'"}***

Even when keyring is correctly installed ansible cannot reference the python keyring library with 'import keyring' from inside community.general.keyring. It seems that ansible has problems with python libraries installed outside of the ansible context. Maybe community.general has to be installed using requirements.txt together with pip env in order to work!?

Different python paths did not work:

```cli
ANSIBLE_PYTHON_INTERPRETER=/usr/local/bin/python3 ansible-playbook playbook_keyring.yml

ANSIBLE_PYTHON_INTERPRETER=/usr/bin/python3 ansible-playbook playbook_keyring.yml
```

## A simple solution without using community.general.keyring

Use Keyring to set a 'test' acount with label 'test':

```cli
keyring set test test
keyring get test test
```

Use get_pass.sh with macOS 'security' cli tool or get_pass.py with keyring to retrieve a password.

Remember to chmod scripts:

```cli
chmod +x get_pass.sh
chmod +x get_pass.py
```

Test of pipe func with get_pass scripts:

```cli
ansible-playbook playbook_pipe.yml
```

Afterwards you use this with 'ansible_become_pass' in an inventory / host file or any other yaml file like this:

```yaml
ansible_become_pass="{{ lookup('pipe', './get_pass.py') }}"
```

## Using ansible-vault vault-keyring.py and vault-keyring-client.py with macOS Keyring / keychain

This is a new type of vault-password script  (a 'client') that takes advantage of and enhances the multiple vault password support.

If a vault password script basename ends with the name '-client', consider it a vault password script client.

A vault password script 'client' just means that the script will take a '--vault-id' command line arg.

The previous vault password script (as invoked by --vault-password-file pointing to an executable) takes no args and returns the password on stdout. But it doesnt know anything about --vault-id or multiple vault passwords.

The new 'protocol' of the vault password script takes a cli arg ('--vault-id') so that it can lookup that specific vault-id and return it's password.

Since existing vault password scripts don't know the new 'protocol', a way to distinguish password scripts that do understand the protocol was needed.  The convention now is to consider password scripts that are named like 'something-client.py' (and executable) to be vault password client scripts.

The new client scripts get invoked with the '--vault-id' they were requested for. An example:

```cli
     ansible-playbook --vault-id my_vault_id@contrib/vault/vault-keyring-client.py some_playbook.yml
```

That will cause the 'contrib/vault/vault-keyring-client.py' script to be invoked as:

```cli
     contrib/vault/vault-keyring-client.py --vault-id my_vault_id
```

The previous vault-keyring.py password script was extended to become vault-keyring-client.py. It uses the python 'keyring' module to request secrets from various backends. The plain 'vault-keyring.py' script
would determine which key id and keyring name to use based on values that had to be set in ansible.cfg. So it was also limited to one keyring name.

The new vault-keyring-client.py will request the secret for the vault id provided via the '--vault-id' option.
The script can be used without config and can be used for multiple keyring ids (and keyrings).

On success, a vault password client script will print the password to stdout and exit with a return code of 0.
If the 'client' script can't find a secret for the --vault-id, the script will exit with return code of 2 and print an error to stderr.  

### Files

playbook_pipe.yml  
playbook_vault.yml  
/vars/api_key.yml
vault-keyring.py
vault-keyring-client.py

### Initilise scripts

The original ansible-vault scripts are found in community.general scripts/vault folder (ie. ~/.ansible/collections/ansible_collections/community/general/scripts/vault/)

Copy vault-keyring.py and vault-keyring-client.py to your project or your ansible folder outside source control (~/.ansible/).

Change the python shebang line in vault-keyring.py and vault-keyring-client.py to reflect your python 3 path (#!/usr/bin/env python3).

### Save scripts with the executable bit set

```cli
chmod +x vault-keyring.py vault-keyring-client.py
```

### Setup password with vault-keyring.py with the creditals in ansible.cfg

```cli
[defaults]
vault_password_file = vault-keyring.py

[vault]
keyname = ansible_key_test
username = test_user
```

```cli
./vault-keyring.py set
```

or

### Setup password with vault-keyring-client.py

```cli
./vault-keyring-client.py --vault-id 'ansible_key_test'  --username 'test_user' --set
```

### Test set password with vault-keyring.py (default option = get)

```cli
./vault-keyring.py
```

### Test set password with vault-keyring-client.py

```cli
./vault-keyring-client.py --vault-id 'ansible_key_test'  --username 'test_user'
```

### Encrypt vars with set password

```cli
ansible-vault encrypt vars/api_key.yml
```

### Test ansible-vault with vault-keyring.py

vault-keyring.py is automaticly used when defined in ansible.cfp

```cli
ansible-vault view vars/api_key.yml --vault-password-file vault-keyring.py
```

The below will also work as ansible-vault will automaticly detect and decrypt the vars/api_key.yml file with vault-keyring.py

```cli
ansible-vault view vars/api_key.yml
```

### Test ansible-vault with vault-keyring-client.py

```cli
ansible-vault view vars/api_key.yml --vault-id ansible_key_test@vault-keyring-client.py
```

***ToDo:*** Somehow ansible-vault with vault-keyring-client.py cannot see the test_user in ansible.cfg but uses the current system $USER!?

### Use with ansible-playbook with vault-keyring.py

```cli
ansible-playbook playbook_vault.yml --vault-password-file vault-keyring.py
```

```cli
ansible-playbook --vault-id vault-keyring.py playbook_vault.yml
```

vault-keyring.py is automaticly detected and used when the credentials is defined in ansible.cfg, so this will also work:

```cli
ansible-playbook playbook_vault.yml
```

### Use with ansible-playbook with vault-keyring-client.py

```cli
ansible-playbook --vault-id ansible_key_test@vault-keyring-client.py playbook_vault.yml
```

ToDo: Somehow ansible-playbook used with vault-keyring-client.py cannot see the test_user in ansible.cfg but uses the current system $USER!?

Reproduces the same error as above:
**ERROR! Vault password client script ~/.ansible/vault-keyring-client.py did not find a secret for vault-id=ansible_key_test: b'vault-keyring-client could not find key="ansible_key_test" for user="$USER" via backend="macOS Keyring"\n'**

It turns out that vault-keyring-client.py and vault-keyring.py uses to different methods to get 'username'! vault-keyring.py works nicely and the other one not!

**NB** Not sure if the username issue here relates to the this keyring issue specif for  macOS:
[Implement API for retrieving usernames](https://github.com/jaraco/keyring/issues/400)

## Notes

**NB!** It's recommended to put any password files / scripts outside the current folder for security reasons - example path: ***~/.ansible***

## References

[ansible-vault](https://docs.ansible.com/ansible/latest/cli/ansible-vault.html)  
[Encrypting content with Ansible Vault](http://docs.ansible.com/ansible/2.10/user_guide/vault.html)  
[community.general/scripts/vault](https://github.com/ansible-collections/community.general/blob/main/scripts/vault/)

## Similar projects

[ansible-autosetup](https://github.com/laurent-kling/ansible-autosetup)  
[vaultkeychain](https://github.com/gitinsky/vaultkeychain)  
[vault-unseal](https://github.com/covermymeds/vault_unseal)  

[ansible-tools](https://github.com/lvillani/ansible-tools)  

[VSCode ansible-vault extension](https://github.com/dhoeric/vscode-ansible-vault)  
[Ansible Modules Hashivault](https://github.com/TerryHowe/ansible-modules-hashivault)
