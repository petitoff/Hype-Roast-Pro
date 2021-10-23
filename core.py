import cbpro
from telegram import *
from telegram.ext import *

import json
from threading import Thread

# Global variables

# Import keys to api coinbase pro and telegram
with open("keys.json", 'r') as f:
    api_keys = json.loads(f.read())
    coinbase_pro_public_key = api_keys["coinbase-pro"]["public"]
    coinbase_pro_pass_key = api_keys["coinbase-pro"]["pass"]
    coinbase_pro_secret_key = api_keys["coinbase-pro"]["secret"]

    telegram_settings_api_main = api_keys["telegram"]["settings"]
    telegram_alert_api_main = api_keys["telegram"]["alert"]

auth_client = cbpro.AuthenticatedClient(coinbase_pro_public_key, coinbase_pro_secret_key, coinbase_pro_pass_key)

public_client = cbpro.PublicClient()

""" Auxiliary functions """
# Downloading all information about cryptocurrencies.
result_about_all_cryptocurrencies = public_client.get_products()
print(result_about_all_cryptocurrencies[0])
print(public_client.get_product_ticker("BTC-EUR"))
print(public_client.get_product_24hr_stats("BTC-EUR"))
# for result in result_about_all_cryptocurrencies:
#     print(result["id"])

""" Main Function """


# Live cryptocurrency price
def live_price_cryptocurrency():
    pass


""" Telegram """


def start_command(update, context):
    update.message.reply_text(
        "This is premium private bot. You can't use it without permission")
    # json_id = update
    # id_of_chat = json_id["message"]["chat"]["id"]
    # print(id_of_chat)


def help_command(update, context):
    update.message.reply_text("If you want help, type help.")


def status_command(update, context):
    update.message.reply_text("I'm alive and well.")


def settings_and_functions(update, context):
    json_id = update

    if json_id["message"]["chat"]["id"] != 1181399908:
        update.message.reply_text("You don't have permission.")
        return

    text = str(update.message.text).lower()
    if text[:5] == "price":
        pass


bot_settings = Bot(telegram_settings_api_main)
bot_alert = Bot(telegram_alert_api_main)


def telegram_main():
    # updater = Updater(telegram_api_main, use_context=True)  # main
    # updater = Updater(telegram_api_dev, use_context=True)  # for dev and test

    updater = Updater(telegram_settings_api_main, use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start_command))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("status", status_command))

    dp.add_handler(MessageHandler(Filters.text, settings_and_functions))

    updater.start_polling(1)
