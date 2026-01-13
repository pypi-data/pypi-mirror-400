# README

This is my hackmud chat API module, as a module.

It is designed to be gotten as a package from PyPI via `pip`, but I believe you can copy the `hackmudChatAPI` folder into your workspace and use it as a module like that.

Better usage docs coming sometime in the future.

## Usage

Place this at the start of your python file:

```py
from hackmudChatAPI import ChatAPI

chat = ChatAPI()
```

You can get a new token in your config file without additional code using `python -m hackmudChatAPI` with the package installed.

This will assume the default config file location of `projectDir/config.json`.

If you store the config file elsewhere, a symlink to that will work.

More details will come sometime in the future.
