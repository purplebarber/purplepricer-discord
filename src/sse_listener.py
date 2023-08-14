from json import loads
import sseclient
import requests
from src.http import HTTP
from src.config import Config
from src.webhook import Webhook
from src.database import Database

DB_NAME = "src/prices.db"


class SSEListener:
    def __init__(self):
        self.config = Config()
        self.webhook = Webhook()
        self.http = HTTP()
        self.sse_url = self.config.sse_url
        self.headers = self.config.headers
        self.params = self.config.params
        self.database = Database(db_name=DB_NAME, table_name="prices")

    async def update_pricelist(self) -> None:
        prices = await self.http.get(self.config.pricelist_url, headers=self.config.headers, params=self.config.params)

        if not prices:
            return

        prices = prices.get("items")

        for sku, item in prices.items():
            name = item.get("name")
            buy = item.get("buy")
            sell = item.get("sell")

            if not sku or not name or not buy or not sell:
                continue

            self.database.insert_item_data(sku, {"name": name, "buy": buy, "sell": sell,
                                                 "old_buy": buy, "old_sell": sell})

    def sse_request(self):
        return requests.get(self.sse_url, stream=True, headers=self.headers, params=self.params)

    async def listen_and_update(self) -> None:
        response = self.sse_request()
        client = sseclient.SSEClient(response)
        for event in client.events():
            if not event.event == "price":
                print("Event not price")
                continue

            data = loads(event.data)
            sku = data.get("sku")
            name = data.get("name")
            buy = data.get("buy")
            sell = data.get("sell")

            if not sku or not name or not buy or not sell:
                print("Missing data")
                continue

            old_item_data = self.database.get_item_data(sku)
            if not old_item_data:
                old_item_data = {"name": name, "buy": buy, "sell": sell,
                                 "old_buy": buy, "old_sell": sell}

            await self.webhook.send_webhooks_to_urls(sku, name, old_item_data)
            self.database.insert_item_data(sku, {"name": name, "buy": buy, "sell": sell,
                                                 "old_buy": old_item_data.get("buy"),
                                                 "old_sell": old_item_data.get("sell")})

    async def close(self) -> None:
        await self.webhook.close()
        self.sse_request().close()
