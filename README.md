# ansible-keyring

Access ansible passwords securely from keyring / Mac keychain without ressorting to [ansible-vault](https://docs.ansible.com/ansible/latest/cli/ansible-vault.html).

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

Check keyring doc's

```cli
ansible-doc -t lookup keyring
```

### Ressources

[Docs Community.General](https://docs.ansible.com/ansible/latest/collections/community/general/)

### Problems

Ansible apparently cannot reference the python library with 'import keyring' from inside community.general.keyring. It seems that ansible has problems with python libraries installed outside of the ansible contest. Maybee it has to be installed using requirements.txt to work!?

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

```cli
ansible_become_pass="{{ lookup('pipe', './get_pass.py') }}"
```

**NB!** It's recommended to put any password files / scripts outside the current folder for security reasons - example path: ***~/.ansible***
