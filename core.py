import cbpro
from telegram import *
from telegram.ext import *

import json

import time
from datetime import datetime, timedelta

from threading import Thread

# Global variables

# Authorized chat id that the bot can communicate with and that can be used to change settings in a specific bot.
chat_id_right = 1181399908

# Variable that allows you to stop the function of sending live price of the cryptocurrency
time_update = 600
time_update_stop = False

list_all_availabe_crypto_euro = []
list_crypto_to_live_price_alert = ["BTC-EUR"]

# Import keys to api coinbase pro and telegram
with open("keys.json", 'r') as f:
    api_keys = json.loads(f.read())
    coinbase_pro_public_key = api_keys["coinbase-pro"]["public"]
    coinbase_pro_pass_key = api_keys["coinbase-pro"]["pass"]
    coinbase_pro_secret_key = api_keys["coinbase-pro"]["secret"]

    telegram_settings_api_main = api_keys["telegram"]["settings"]
    telegram_alert_api_main = api_keys["telegram"]["alert"]

auth_client = cbpro.AuthenticatedClient(
    coinbase_pro_public_key, coinbase_pro_secret_key, coinbase_pro_pass_key)

public_client = cbpro.PublicClient()

""" Auxiliary and testing functions """
# Downloading all information about cryptocurrencies.
result_about_all_cryptocurrencies = public_client.get_products()

# print(result_about_all_cryptocurrencies[0])
# print(public_client.get_product_ticker("BTC-EUR"))
# print(public_client.get_product_24hr_stats("BTC-EUR"))

# startdate = (datetime.now() - timedelta(seconds=60*60*200)
#              ).strftime("%Y-%m-%dT%H:%M")
# enddate = datetime.now().strftime("%Y-%m-%dT%H:%M")

# print(startdate)
# print(enddate)

# result1 = public_client.get_product_historic_rates(
#     'BTC-USD',
#     start=startdate,
#     end=enddate,
#     granularity=3600)


def percentage_calculator(current_price, start_price):
    current_price = float(current_price)
    start_price = float(start_price)
    percentage = ((current_price - start_price) / start_price) * 100
    percentage = round(percentage, 2)
    return percentage


def get_list_of_all_crypto_to_euro():
    global list_all_availabe_crypto_euro

    result_about_all_cryptocurrencies = public_client.get_products()
    for result in result_about_all_cryptocurrencies:
        cryptocurrency = result["id"]
        index_of_char = cryptocurrency.index("-")
        if cryptocurrency[index_of_char+1:] == "EUR":
            list_all_availabe_crypto_euro.append(cryptocurrency)


def get_price_from_coinbase(name):
    result = public_client.get_product_ticker(name)
    return result


""" Main Function """


def live_price_cryptocurrency():
    global list_all_availabe_crypto_euro, list_crypto_to_live_price_alert

    dct_price_time = {}
    d1 = {}
    start_time = time.time()

    while True:
        if time_update_stop is True:
            # This function can be paused if the user so wishes. This line of code makes it possible.
            while True:
                if time_update_stop is False:
                    break
                time.sleep(10)

        current_time = time.time()
        current_time -= start_time  # how much time has passed
        if current_time >= 86400:
            # If 24 hours have passed, start calculating the price difference from the beginning
            start_time = time.time()
            dct_price_time.clear()

        for name in list_crypto_to_live_price_alert:
            name = name.upper()  # Make sure the name is capitalized
            # Finding the currency sign of the price.
            currency_sign_index = name.index("-")
            currency_sign = name[currency_sign_index+1:]

            if name not in dct_price_time.keys():
                # If the cryptocurrency is not in the dictionary yet, we add it with the initial price
                start_price = get_price_from_coinbase(name)
                start_price = start_price["price"]
                d1[name] = start_price
                dct_price_time.update(d1)

            # Downloading the current price from the api
            current_price = get_price_from_coinbase(name)
            current_price = current_price["price"]
            percentage = percentage_calculator(
                current_price, dct_price_time[name])
            current_price_print = name + " " + \
                str(percentage) + "% | " + \
                str(current_price) + " " + currency_sign

            bot_settings.send_message(
                chat_id=1181399908, text=current_price_print)

        count = 0
        while True:
            count += 1
            if count >= time_update:
                break
            time.sleep(1)


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

    global time_update, time_update_stop

    text = str(update.message.text).lower()
    if text[:5] == "price":
        pass
    elif text[:4] == "time":
        try:
            time_update = int(text[4:])
            time_update = time_update * 60
            update.message.reply_text(f"Time set to: {time_update} seconds")
        except ValueError:
            update.message.reply_text(
                "Enter the time in whole minutes greater than 0.")
    elif text[:6] == "tstart":
        time_update_stop = False
        update.message.reply_text(
            "Send message with live price of crypto is start.")
    elif text[:5] == "tstop":
        time_update_stop = True
        update.message.reply_text(
            "Send message with live price of crypto is stop.")


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
