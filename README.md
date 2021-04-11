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
ANSIBLE_PYTHON_INTERPRETER=/usr/local/bin/python3 ansible-playbook playbook_passwd.yml

ANSIBLE_PYTHON_INTERPRETER=/usr/bin/python3 ansible-playbook playbook_passwd.yml
```

## A simple solution without using community.general.keyring

Use Keyring to set a 'test' acount with label 'test':

```cli
keyring set test test
keyring get test test
```

Use get_pass.sh with macOS 'security' or get_pass.py with keyring to retrieve a password.

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

## Using ansible-vault vault-keyring-client.py with keychain

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

The previous vault-keyring.py password script was extended to become vault-keyring-client.py. It uses
the python 'keyring' module to request secrets from various backends. The plain 'vault-keyring.py' script
would determine which key id and keyring name to use based on values that had to be set in ansible.cfg.
So it was also limited to one keyring name.

The new vault-keyring-client.py will request the secret for the vault id provided via the '--vault-id' option.
The script can be used without config and can be used for multiple keyring ids (and keyrings).

On success, a vault password client script will print the password to stdout and exit with a return code of 0.
If the 'client' script can't find a secret for the --vault-id, the script will exit with return code of 2 and print an error to stderr.

Files:  
playbook_vault.yml  
/vars/api_key.yml

```cli
ansible-vault encrypt vars/api_key.yml
```
Password: test

Test vault password:

```cli
ansible-playbook playbook_vault.yml --ask-vault-pass
```

```cli
ansible-playbook playbook_vault.yml --vault-password-file get_pass.py
```

--vault-id examples:

Test vault-keyring-client.py:

```cli
python3 vault-keyring-client.py --vault-id test  --username test
```

Result: test

```cli
ansible-playbook --vault-id get_pass.py playbook_vault.yml
```

```cli
ansible-playbook --vault-id test@contrib/vault/vault-keyring-client.py playbook_vault.yml
```

## Notes

**NB!** It's recommended to put any password files / scripts outside the current folder for security reasons - example path: ***~/.ansible***

## References

[ansible-vault](https://docs.ansible.com/ansible/latest/cli/ansible-vault.html)  
[ansible-tools](https://github.com/lvillani/ansible-tools)  
[Encrypting content with Ansible Vault](http://docs.ansible.com/ansible/2.10/user_guide/vault.html)
