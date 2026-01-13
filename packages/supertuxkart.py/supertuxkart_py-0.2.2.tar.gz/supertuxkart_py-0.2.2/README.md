# SuperTuxKart Online Service API Wrapper
![Python Version from PEP 621 TOML](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fcodeberg.org%2FlinaSTK%2Fstk.py%2Fraw%2Fbranch%2Fmain%2Fpyproject.toml)
![PyPI - License](https://img.shields.io/pypi/l/supertuxkart.py)
![Gitea Stars](https://img.shields.io/gitea/stars/linaSTK/stk.py?gitea_url=https%3A%2F%2Fcodeberg.org&style=flat)
![Gitea Last Commit](https://img.shields.io/gitea/last-commit/linaSTK/stk.py?gitea_url=https%3A%2F%2Fcodeberg.org)

A library that allows for interacting with teh SuperTuxKart Online Service ("STKAddons") API.

# Install
You can install supertuxkart.py using the following command:
```
pip install supertuxkart.py
```
... or if you want to use the git/development version:
```
pip install git+https://codeberg.org/linaSTK/stk.py
```

# Example:
```py
>>> import supertuxkart
>>> client = supertuxkart.SuperTuxKartClient(userid=513714, token="<token here>")
>>> # You can also use username/password auth, though
>>> # userid/token is prioritized if both specified
>>> client = supertuxkart.SuperTuxKartClient(username="Sayori", password="password")
>>> session = client.account.authorize()
>>> session
<SessionInfo token=xxxxxxxxxxxxxxxxxxxxxxxx username=Sayori realname=Sayori userid=513714 achieved=[2, 3, 5, 7, 8, 9]>
```

# License
This project is licensed under the MIT license.
