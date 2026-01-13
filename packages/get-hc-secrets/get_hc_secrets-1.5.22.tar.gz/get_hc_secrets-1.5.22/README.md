# getSecrets package

getSecrets is a simple package that reads from the given engine ('secret' by default) of a Hashicorp vault
It can also read data from the local vault.yml file

usage:

```
from getSecrets import *

data = get_secret(<id>, [repo:<secret>])

usr, pwd = get_user_pwd(<id> , [repo:<secret>])

updater = update_secret(<id>, <new_object>, [repo:<secret>])

list = list_secret([<secret>]

```

Vault parameters are stored in a config file ~/.config/.vault/.vault.yml

```
vault:
  token: "<access token>"
  vault_addr: "https://vault:8200"
  certs: "<path>/bundle.pem"
 
id:
  item1: 1
  item2: 2
  username: user
  password: !@•?
```

for reminder:
bundle.pem, for own certificates, is made of, in this order:

- vault certificate
- intermediate certificate
- root certificate