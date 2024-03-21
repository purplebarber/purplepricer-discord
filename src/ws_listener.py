import socketio
from json import loads
from src.http import HTTP
from src.config import Config
from src.webhook import Webhook
from src.database import Database
from asyncio import sleep, Queue, create_task

DB_NAME = "src/prices.db"


class WSListener:
    def __init__(self):
        self.config = Config()
        self.webhook = Webhook()
        self.http = HTTP()
        self.uri = self.config.sse_url

        # Socket.IO setup
        self.sio = socketio.AsyncClient()
        self.database = Database(db_name=DB_NAME, table_name="prices")

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
                create_task(self.webhook.send_webhooks_to_urls(sku_queue, name_queue, item_data_queue))
                webhook_queue.task_done()

        create_task(process_webhooks())

        await self.sio.connect(self.uri, auth=self.config.headers.get('Authorization'))

        @self.sio.on('price')
        async def message(data):  # Handle incoming messages
            sku = data.get("sku")
            name = data.get("name")
            buy = data.get("buy")
            sell = data.get("sell")

            if not sku or not name or not buy or not sell:
                print("Missing data")
                return

            old_item_data = self.database.get_item_data(sku)
            if not old_item_data:
                old_item_data = {"name": name, "buy": buy, "sell": sell,
                                 "old_buy": buy, "old_sell": sell}

            item_data = {"name": name, "buy": buy, "sell": sell,
                         "old_buy": old_item_data.get("buy"),
                         "old_sell": old_item_data.get("sell")}

            self.database.insert_item_data(sku, item_data)
            await webhook_queue.put((sku, name, item_data))

        await self.sio.wait()

    async def close(self) -> None:
        await self.webhook.close()
        await self.sio.disconnect()  # Close Socket.IO connection
