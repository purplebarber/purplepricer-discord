from src.database import Database
from math import floor, ceil


DB_NAME = "src/prices.db"


# database for storing prices.tf data
db = Database(db_name=DB_NAME, table_name="prices")


def get_key_buy_price() -> dict:
    key_dict = db.get_item_data("5021;6")
    return key_dict.get("buy")


def get_key_sell_price() -> dict:
    key_dict = db.get_item_data("5021;6")
    return key_dict.get("sell")


def get_key_buy_price_in_half_scrap() -> int:
    key_dict = db.get_item_data("5021;6")
    return to_half_scrap(key_dict.get("buy").get("metal"))


def get_key_sell_price_in_half_scrap() -> int:
    key_dict = db.get_item_data("5021;6")
    return to_half_scrap(key_dict.get("sell").get("metal"))


def convert_currency_dict_to_half_scrap(currency: dict) -> float:
    if "metal" in currency:
        metal = currency.get('metal')
    else:
        metal = 0

    if "keys" in currency:
        keys = currency.get('keys')
    else:
        keys = 0
    ref_in_half_scrap = to_half_scrap(metal)
    keys_in_half_scrap = keys * get_key_sell_price_in_half_scrap()

    total_half_scrap = ref_in_half_scrap + keys_in_half_scrap
    return total_half_scrap


def convert_half_scrap_to_currency_dict(half_scrap_count: int) -> dict:
    refined_count = to_refined(half_scrap_count)
    current_key_sell_price = get_key_sell_price_in_half_scrap()
    refined_count_in_half_scrap = to_half_scrap(refined_count)

    amount_of_ref_in_half_scrap = refined_count_in_half_scrap % current_key_sell_price
    amount_of_keys = round((refined_count_in_half_scrap - amount_of_ref_in_half_scrap) / current_key_sell_price)

    amount_of_ref = to_refined(amount_of_ref_in_half_scrap)

    return {'metal': amount_of_ref, 'keys': amount_of_keys}


def refinedify(number_to_convert: float) -> float:
    return (
        floor((round(number_to_convert * 18, 0) * 100) / 18) / 100
        if number_to_convert > 0
        else ceil((round(number_to_convert * 18, 0) * 100) / 18) / 100
    )


def to_half_scrap(refined: float) -> int:
    return ceil(refined * 18)


def to_refined(half_scrap: int) -> float:
    return refinedify(floor(half_scrap / 18 * 100) / 100)