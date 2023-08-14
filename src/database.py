import sqlite3
from json import dumps, loads


class Database:
    def __init__(self, db_name='database_path.db', table_name='unnamed'):
        self.db_name = db_name
        self.table_name = table_name
        self._create_table()

    def _create_table(self) -> None:
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {self.table_name} (
                sku TEXT PRIMARY KEY,
                data TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def insert_item_data(self, sku: str, item_data: dict) -> None:
        data_str = dumps(item_data)

        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute(f'''
            INSERT OR REPLACE INTO {self.table_name} (sku, data)
            VALUES (?, ?)
        ''', (sku, data_str))
        conn.commit()
        conn.close()

    def get_item_data(self, sku: str) -> dict | None:
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute(f'''
            SELECT data FROM {self.table_name} WHERE sku = ?
        ''', (sku,))
        data_str = cursor.fetchone()
        conn.close()

        if data_str is not None:
            return loads(data_str[0])
        else:
            return None

    def delete_item_data(self, sku: str) -> None:
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute(f'''
            DELETE FROM {self.table_name} WHERE sku = ?
        ''', (sku,))
        conn.commit()
        conn.close()

    def get_all_item_data(self) -> dict:
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute(f'''
            SELECT sku, data FROM {self.table_name}
        ''')
        rows = cursor.fetchall()
        conn.close()

        item_data_dict = dict()
        for row in rows:
            sku, data_str = row
            item_data = loads(data_str)
            item_data_dict[sku] = item_data

        return item_data_dict
