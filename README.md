# ansible-keyring

Access ansible passwords securely from keyring / Mac keychain 

## prerequisites

[keyring](https://pypi.org/project/keyring/) pypi.org 

Install keyring with pip

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
