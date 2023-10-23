from json import loads
from src.http import HTTP
from src.config import Config
from src.webhook import Webhook
from src.database import Database
import aiohttp
from asyncio import sleep, Queue, create_task
from aiohttp_sse_client import client as sse_client

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

        for item in prices.get("items"):
            sku = item.get("sku")
            name = item.get("name")
            buy = item.get("buy")
            sell = item.get("sell")

            if not sku or not name or not buy or not sell:
                continue

            self.database.insert_item_data(sku, {"name": name, "buy": buy, "sell": sell,
                                                 "old_buy": buy, "old_sell": sell})

    async def listen_and_update(self) -> None:
        webhook_queue = Queue()

        async def process_webhooks():
            while True:
                sku_queue, name_queue, item_data_queue = await webhook_queue.get()
                await self.webhook.send_webhooks_to_urls(sku_queue, name_queue, item_data_queue)
                webhook_queue.task_done()
        create_task(process_webhooks())

        while True:
            try:
                async with sse_client.EventSource(self.sse_url, headers=self.headers, params=self.params)\
                        as event_source:
                    async for event in event_source:
                        if event.message != "price":
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

                        item_data = {"name": name, "buy": buy, "sell": sell,
                                     "old_buy": old_item_data.get("buy"),
                                     "old_sell": old_item_data.get("sell")}

                        self.database.insert_item_data(sku, item_data)
                        await webhook_queue.put((sku, name, item_data))

            except aiohttp.ClientConnectorError as connector_error:
                print(f"Client Connector Error: {connector_error}")
                await sleep(5)

            except Exception as e:
                print(f"Exception: {e}")
                await sleep(5)

    async def close(self) -> None:
        await self.webhook.close()
