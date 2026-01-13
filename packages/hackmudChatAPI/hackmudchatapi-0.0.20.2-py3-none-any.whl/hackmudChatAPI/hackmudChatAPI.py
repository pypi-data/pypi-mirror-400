"""A python implementation of the hackmud chat API, using the requests module."""

from .package_data import CODE_VERSION

__version__ = CODE_VERSION

from .types import ChatMessage, TokenError


class ChatAPI:
    # import requests
    # import json
    from sys import path
    from requests import Response

    def __init__(
        self,
        config_file: str = f"{path[0]}/config.json",
        token_refresh: bool = False,
        verbosity: int = 1,
    ):
        self.verbosity = verbosity
        self.token_refresh = token_refresh
        self.config_file = config_file
        self.config: dict

        self.log("Initialising ChatAPI instance...")

        self.log(f"Attempting to load config from {repr(self.config_file)}...")
        try:
            self.load_config()
            self.log("Config successfully loaded.")
        except FileNotFoundError:

            self.log(f"Config file not found at {repr(self.config_file)}.")

            self.log("Setting base config...")
            self.config = {
                "url": "https://www.hackmud.com",
                "header": {"Content-Type": "application/json"},
                "ErrorOnBadToken": False,
            }

            self.log(f"Creating new config file at {repr(self.config_file)}...")
            self.save_config()
            self.log("New config file created.")
            self.load_config()

            self.get_token()

        if self.config.get("url") is None:
            self.log("API URL not present in config - saving base definition.")
            self.config["url"] = "https://www.hackmud.com"
            self.save_config()

        # self.header: dict = self.config.get("header")

        if self.header is None:
            self.log("API header not present in config - saving base definition.")
            self.config["header"] = {"Content-Type": "application/json"}
            self.header = self.config.get("header", None)
            self.save_config()

        if self.config.get("ErrorOnBadToken") is None:
            self.log("ErrorOnBadToken not present in config - saving base definition.")
            self.config["ErrorOnBadToken"] = True
            self.save_config()

        self.load_config()

        if self.token is None:
            self.log("No chat API token present in config.")
            self.get_token(
                badToken=True, BTReason="no chat API token present in config."
            )

        token_test = self.test_token()

        while not token_test:
            self.log("Token tested bad.")
            token_test = self.get_token(badToken=True, BTReason="bad token.")

        self.log("Retriving account data...")
        self.get_users()
        self.users = self.config.get("users")
        self.log("Account data retrieved.")

        self.log("Instance configuration:")
        self.log(f"Config File: {repr(self.config_file)}")
        self.log(f"API URL: {repr(self.url)}")
        self.log(f"API Header: {repr(self.header)}")
        self.log(f"API Token: {repr(self.token)}", 2)
        self.log(f"Error on Bad Token: {repr(self.config.get("ErrorOnBadToken"))}")
        self.log(f"Users: {repr(self.users)}")
        self.log("ChatAPI instance initialised.")

    def log(self, input, verbosity: int = 1, level: int = 0):
        """
        My logging function.

        Args:
            input (any): The thing being logged.
            verbosity (int, optional): The verbosity level at which it will appear. Defaults to 1.
            level (int, optional): The level/type of the log. Defaults to 0. If a level >5 is given, it will be set to 5.

                The log levels (in order) are:
                - (0) LOG
                - (1) INFO
                - (2) DEBUG
                - (3) WARN
                - (4) ERROR
                - (5) FATAL
        """
        LOG_LEVELS = ["LOG", "INFO", "DEBUG", "WARN", "ERROR", "FATAL"]
        if level > len(LOG_LEVELS) - 1:
            level = len(LOG_LEVELS)
        if self.verbosity >= verbosity:
            print(f"[{LOG_LEVELS[level]}] {input}")

    def test_token(self, token=None):
        import requests

        if token is None:
            token = self.token

        self.log("Testing token...")
        response = requests.post(
            url=f"{self.url}/mobile/account_data.json",
            headers=self.header,
            json={"chat_token": token},
        ).content

        if response == b"":
            self.log("Token invalid.")
            return False
        else:
            self.log("Token valid.")
            return True

    def load_config(self):
        import json

        with open(self.config_file) as f:
            if len(f.read()) == 0:
                raise FileNotFoundError
            else:
                f.seek(0)

            self.config: dict = json.load(f)
            self.url: dict = self.config.get("url", "https://www.hackmud.com")
            self.header: dict = self.config.get("header")
            self.token: str = self.config.get("chat_token")

    def save_config(self):
        import json

        with open(self.config_file, "w") as f:
            json.dump(self.config, f, indent=4)

    def get_token(
        self,
        chat_pass: str | None = None,
        badToken: bool = False,
        BTReason: str = "reason unknown.",
    ) -> bool:
        """
        Gets a chat API token from the inputted chat_pass, which is obtained from running "chat_pass" in-game.

        Args:
            chat_pass (str | None, optional): The chat_pass to get the token from. If one is not given, prompts for it in the terminal. Defaults to None.
            badToken (bool, optional): If a token is being generated due to encountering a bad token. Defaults to False.
            BTReason (str, optional): The reason the token is bad. Defaults to "reason unknown.".

        Raises:
            TokenError: If badToken and the "ErrorOnBadToken" setting are True, a TokenError is raised.

        Returns:
            bool: If a token was successfully generated.
        """

        """
        Gets a chat API token from the inputted chat_pass, which is obtained from running "chat_pass" in-game.

        Args:
            chat_pass (str | None, optional): The chat_pass to get the token from. If one is not given, prompts for it in the terminal. Defaults to None.
        """

        import requests
        import json

        self.load_config()

        if badToken:
            if self.config["ErrorOnBadToken"]:
                raise TokenError(f"Bad chat API token - {BTReason}")
            else:
                self.log("Getting new token (bad token)...")
        else:
            self.log("Getting new token...")

        if not chat_pass:
            chat_pass = input("chat_pass password: ")

        if chat_pass != "":
            self.log("Requesting new token...")
            newToken = json.loads(
                requests.post(
                    url=f"{self.url}/mobile/get_token.json",
                    headers=self.header,
                    json={"pass": chat_pass},
                ).content
            ).get("chat_token", None)

            if self.test_token(newToken):
                self.log("New token generated.")
                self.token = newToken
                self.config["chat_token"] = newToken
                self.save_config()
                self.log("New token saved.")
                if self.token_refresh:
                    quit()
                return True
            else:
                self.log("Bad chat_pass - no new token.")
                self.load_config()
                if self.token_refresh:
                    quit()
                return False

    def get_users(self) -> list[str]:
        import requests
        import json

        self.load_config()

        accountData: dict = json.loads(
            requests.post(
                url=f"{self.url}/mobile/account_data.json",
                headers=self.header,
                json={"chat_token": self.token},
            ).content
        )["users"]

        self.config["users"] = list(accountData.keys())

        self.save_config()
        return accountData

    def send(self, user: str, channel: str, msg: str) -> Response:
        """
        Sends a message from the inputted user to the inputted channel containing the inputted msg.

        Args:
            user (str): The user to send the message from.
            channel (str): The channel to send the message to.
            msg (str): The message to send.
        """
        import requests

        payload = {
            "chat_token": self.token,
            "username": user,
            "channel": channel,
            "msg": msg,
        }

        return requests.post(
            url=f"{self.url}/mobile/create_chat.json",
            headers=self.header,
            json=payload,
        )

    def tell(self, user: str, target: str, msg: str) -> Response:
        """
        Sends a message from the inputted user to the inputted target containing the inputted msg.

        Args:
            user (str): The user to send the message from.
            target (str): The target to send the message to.
            msg (str): The message to send.
        """
        import requests

        payload = {
            "chat_token": self.token,
            "username": user,
            "tell": target,
            "msg": msg,
        }

        return requests.post(
            url=f"{self.url}/mobile/create_chat.json",
            headers=self.header,
            json=payload,
        )

    def read(
        self,
        /,
        after: int | float | None = 60,
        before: int | float | None = None,
        users: list[str] = None,
    ) -> dict[str, list[ChatMessage]]:
        """
        Returns the messages recieved by the inputted users within the given before and after parameters.

        Args:
            after (int | float, optional): Number of seconds before "now". Defaults to 60.
            before (int | float, optional): Number of seconds before "now". Defaults to None.
            users (list[str]): A list of the users who you want to read the recieved messages of. Defaults to all users.

        Returns:
            dict: The "chats" component of the request return content. Is a dictionary of the fetched users and a respective list of messages.
        """
        import requests
        import json
        import time

        now = time.time()

        if not users:
            users = self.users

        payload = {
            "chat_token": self.token,
            "usernames": users,
            "before": ((now - before) if before else None),
            "after": ((now - after) if after else None),
        }

        chats: dict = json.loads(
            requests.post(
                url=f"{self.url}/mobile/chats.json",
                headers=self.header,
                json=payload,
            ).content
        )["chats"]

        return chats


def token_refresh():
    """
    Gets a new token for your config.json.
    """

    ChatAPI(token_refresh=True).get_token()
