from src.http import HTTP
from src.config import Config
from src.currency import convert_currency_dict_to_half_scrap
from typing import Literal
from datetime import datetime


class Webhook:
    def __init__(self):
        self.http = HTTP()
        self.config = Config()
        self.username = self.config.username if self.config.username else "Pricer"
        self.avatar_url = self.config.avatar_url
        self.item_site_url = self.config.item_site_url
        self.item_site_url = self.item_site_url[:-1] if self.item_site_url.endswith("/") else self.item_site_url
        self.webhook_urls = self.config.webhook_urls
        self.key_webhook_urls = self.config.key_webhook_urls

    async def send_post_req(self, url: str, sku: str, item_name: str,
                            buying_for_desc: str, selling_for_desc: str,
                            buying_name: str, selling_name: str) -> None:
        webhook_data = {
            "username": self.username,
            "avatar_url": self.avatar_url,
            "content": '',
            "embeds": [
                {
                    "author": {
                        "name": item_name,
                        "url": f"{self.item_site_url}/{sku}",
                        "icon_url": self.avatar_url
                    },
                    "color": 16735095,
                    "fields": [
                        {
                            "name": buying_name,
                            "value": buying_for_desc,
                            "inline": False
                        },
                        {
                            "name": selling_name,
                            "value": selling_for_desc,
                            "inline": False
                        },
                    ],
                    "footer": {
                        "text": f"{sku} 🎀 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
                    }
                }
            ]
        }

        await self.http.post(url, json=webhook_data)

    @staticmethod
    async def make_description_change_string(old_prices: dict, new_prices: dict,
                                             intent: Literal["buy", "sell"]) -> dict:
        old_prices_dict = old_prices
        new_prices_dict = new_prices

        old_prices = convert_currency_dict_to_half_scrap(old_prices)
        new_prices = convert_currency_dict_to_half_scrap(new_prices)

        def convert_currency_to_text(currency_dict: dict) -> str:
            return_string = str()
            if not currency_dict:
                return return_string

            if "keys" in currency_dict:
                return_string += f"{currency_dict.get('keys')} keys"

            if "keys" in currency_dict and "metal" in currency_dict:
                return_string += ", "

            if "metal" in currency_dict:
                return_string += f"{currency_dict.get('metal')} ref"

            return return_string

        old_prices_text = convert_currency_to_text(old_prices_dict)
        new_prices_text = convert_currency_to_text(new_prices_dict)

        # when price stays the same
        if old_prices == new_prices:
            if intent == "buy":
                return {
                    "name": "Buying for 🔄",
                    "value": convert_currency_to_text(new_prices_dict),
                }
            elif intent == "sell":
                return {
                    "name": "Selling for 🔄",
                    "value": convert_currency_to_text(new_prices_dict),
                }

        # when price goes down
        if old_prices > new_prices:
            if intent == "buy":
                return {
                    "name": "Buying for 📉",
                    "value": f"{old_prices_text} ➡ {new_prices_text}",
                }
            elif intent == "sell":
                return {
                    "name": "Selling for 📉",
                    "value": f"{old_prices_text} ➡ {new_prices_text}",
                }

        # when price goes up
        if old_prices < new_prices:
            if intent == "buy":
                return {
                    "name": "Buying for 📈",
                    "value": f"{old_prices_text} ➡ {new_prices_text}",
                }
            elif intent == "sell":
                return {
                    "name": "Selling for 📈",
                    "value": f"{old_prices_text} ➡ {new_prices_text}",
                }

    async def send_webhooks_to_urls(self, sku: str, item_name: str, item_data: dict) -> None:
        buying_for_desc = await self.make_description_change_string(
            item_data["old_buy"], item_data["buy"], "buy"
        )
        selling_for_desc = await self.make_description_change_string(
            item_data["old_sell"], item_data["sell"], "sell"
        )
        for url in self.webhook_urls:
            await self.send_post_req(
                url, sku, item_name, buying_for_desc["value"], selling_for_desc["value"],
                buying_for_desc["name"], selling_for_desc["name"]
            )

        if sku != "5021;6":
            return

        for url in self.key_webhook_urls:
            await self.send_post_req(
                url, sku, item_name, buying_for_desc["value"], selling_for_desc["value"],
                buying_for_desc["name"], selling_for_desc["name"]
            )

    async def close(self):
        await self.http.close()
