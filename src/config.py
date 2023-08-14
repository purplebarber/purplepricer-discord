from json import load


CONFIG_FILE = "config.json"


class Config:
    def __init__(self):
        with open(CONFIG_FILE, "r") as config_json:
            self.config = load(config_json)

        self.pricelist_url = self.config["pricelist_url"]
        self.sse_url = self.config["pricer_sse_url"]
        self.headers = self.config["extra_headers"]
        self.params = self.config["extra_params"]
        self.webhook_urls = self.config["discord_webhook_urls"]
        self.key_webhook_urls = self.config["key_discord_webhook_urls"]
        self.username = self.config["username"]
        self.avatar_url = self.config["avatar_url"]
        self.item_site_url = self.config["item_site_url"]

    def __getitem__(self, key: str):
        return self.config.get(key, None)

    def __setitem__(self, key: str, value):
        self.config[key] = value
