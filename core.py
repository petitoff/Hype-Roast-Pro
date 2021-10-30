import cbpro
from telegram import *
from telegram.ext import *

import json
import time
from datetime import datetime, timedelta
import numpy as np
from threading import Thread

# Global variables

# Authorized chat id that the bot can communicate with and that can be used to change settings in a specific bot.
chat_id_right = 1181399908

time_update = 600  # Every how many seconds the cryptocurrency price from the "live price" function has been sent
time_update_stop = False  # Variable that stores information whether the live price is to be displayed or to be paused
currency_main = "EUR"  # The global currency to which the program adjusts. It is possible to change by telegram

list_all_available_crypto_euro = []
list_all_available_crypto_usdt = []
list_all_available_crypto_usd = []
list_crypto_to_live_price_alert = ["BTC-USD"]

# A dictionary responsible for keeping information about when to notify when a given amount has been reached
dct_break_point = {}

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
    global list_all_available_crypto_euro, result_about_all_cryptocurrencies

    for result in result_about_all_cryptocurrencies:
        cryptocurrency = result["id"]
        index_of_char = cryptocurrency.index("-")
        if cryptocurrency[index_of_char + 1:] == "EUR":
            list_all_available_crypto_euro.append(cryptocurrency)


def get_list_of_all_crypto_to_tether():
    global list_all_available_crypto_usdt, result_about_all_cryptocurrencies

    for result in result_about_all_cryptocurrencies:
        cryptocurrency = result["id"]
        index_of_char = cryptocurrency.index("-")
        if cryptocurrency[index_of_char + 1:] == "USDT":
            list_all_available_crypto_usdt.append(cryptocurrency)


def get_list_of_all_crypto_to_usd():
    global list_all_available_crypto_usd, result_about_all_cryptocurrencies

    for result in result_about_all_cryptocurrencies:
        cryptocurrency = result["id"]
        index_of_char = cryptocurrency.index("-")

        if cryptocurrency[index_of_char + 1:] == "USD":
            list_all_available_crypto_usd.append(cryptocurrency)


def get_price_from_coinbase(name):
    result = public_client.get_product_ticker(name)
    return result


""" Main Function """


def live_price_cryptocurrency():
    global list_all_available_crypto_euro, list_crypto_to_live_price_alert

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
            currency_sign = name[currency_sign_index + 1:]

            if name not in dct_price_time.keys():
                # If the cryptocurrency is not in the dictionary yet, we add it with the initial price
                start_price = get_price_from_coinbase(name)
                start_price = start_price["price"]
                d1[name] = start_price
                dct_price_time.update(d1)

            # Downloading the current price from the api
            current_price = get_price_from_coinbase(name)
            current_price = current_price["price"]
            # Calculation of the price difference
            percentage = percentage_calculator(
                current_price, dct_price_time[name])
            current_price_print = name + " " + str(percentage) + "% | " + str(current_price) + " " + currency_sign

            bot_alert.send_message(
                chat_id=1181399908, text=current_price_print)

        count = 0
        while True:
            count += 1
            if count >= time_update:
                break
            time.sleep(1)


def break_point():
    global dct_break_point

    while True:
        for currency_name in dct_break_point:
            price = public_client.get_product_ticker(currency_name)["price"]

            # checking for upper value
            try:
                price_break_up = dct_break_point[currency_name]["up"]
                if price >= price_break_up and dct_break_point[currency_name]["notify"] is False:
                    bot_alert.send_message(chat_id_right, f"Alert price for sell! | {currency_name} is {price}")
                    dct_break_point.update({currency_name: {"notify": True}})
            except KeyError:
                pass
            # checking for down value
            try:
                price_break_down = dct_break_point[currency_name]["down"]
                if price >= price_break_down and dct_break_point[currency_name]["notify"] is False:
                    bot_alert.send_message(chat_id_right, f"Alert price for buy! | {currency_name} is {price}")
                    dct_break_point.update({currency_name: {"notify": True}})
            except KeyError:
                pass

        time.sleep(10)


class BigDifferencesInPrices:
    global list_all_available_crypto_usd, public_client

    def __init__(self):
        self.dct_start_name_price = {}
        self.dct_notify_name_price = {}

    # The class responsible for examining large price differences.
    def main_function(self):
        start_time = time.time()
        self.start_name_price_append_to_dct()

        while True:
            current_time = time.time()
            current_time -= start_time

            if current_time >= 86400:
                self.start_name_price_append_to_dct()
                start_time = time.time()

            for name_crypto in list_all_available_crypto_usdt:
                try:
                    price_current = public_client.get_product_ticker(name_crypto)["price"]
                    price_start = self.dct_start_name_price[name_crypto]
                except KeyError:
                    continue

                # the percentage by which the price has increased or decreased
                price_deference = percentage_calculator(price_current, price_start)
                # self.dct_start_name_price.update({name_crypto: {"percentage": price_deference}})

                if price_deference >= 10 or price_deference <= -10:
                    self.sending_notifications(name_crypto, price_current, price_deference)
            time.sleep(60)

    def start_name_price_append_to_dct(self):
        for name_crypto in list_all_available_crypto_usd:
            try:
                price_current = public_client.get_product_ticker(name_crypto)["price"]
                self.dct_start_name_price.update({name_crypto: price_current})
            except KeyError:
                continue

    def sending_notifications(self, name_crypto, price_current, percentage):
        try:
            if price_current == self.dct_notify_name_price[name_crypto]:
                pass
        except KeyError:
            pass

        self.dct_notify_name_price.update({name_crypto: price_current})
        if percentage > 0:
            bot_alert.send_message(chat_id_right, f"Growth notification! "
                                                  f"{name_crypto} {percentage} | "
                                                  f"{price_current}")


class TransactionsBuyAndSell:
    # The class responsible for buying and selling
    """ Authenticates, checks balances, places orders. """
    pass


class History:
    def __init__(self):
        self.avg1 = 50
        self.avg2 = 100

    def signal(self):
        self.startdate = (datetime.now() - timedelta(seconds=60 * 60 * 200)).strftime("%Y-%m-%dT%H:%M")
        self.enddate = datetime.now().strftime("%Y-%m-%dT%H:%M")

        self.data = public_client.get_product_historic_rates(
            'SHIB-USDT',
            start=self.startdate,
            end=self.enddate,
            granularity=3600
        )
        self.data.sort()
        self.data.sort(key=lambda x: x[0])

        print(np.mean([x[4] for x in self.data[-self.avg1:]]) > np.mean([x[4] for x in self.data[-self.avg2:]]))
        if np.mean([x[4] for x in self.data[-self.avg1:]]) > np.mean([x[4] for x in self.data[-self.avg2:]]):
            return True
        else:
            return False


class PricePredictionAlgorithms:
    def __init__(self):
        self.avg1 = 50
        self.avg2 = 100

    def runner(self):
        pass

    def main(self, number):
        if number[:8] == "simple-1":
            result = self.simple_algo()
            if result is True:
                return "The last 50 cycles have an average greater than 100 cycles. I recommend buying."
            else:
                return "The last 50 cycles have a lower average than 100 cycles. I recommend selling"

    def simple_algo(self):
        startdate = (datetime.now() - timedelta(seconds=60 * 60 * 200)).strftime("%Y-%m-%dT%H:%M")
        enddate = datetime.now().strftime("%Y-%m-%dT%H:%M")

        data = public_client.get_product_historic_rates(
            'SHIB-USDT',
            start=startdate,
            end=enddate,
            granularity=3600
        )
        data.sort()
        data.sort(key=lambda x: x[0])

        if np.mean([x[4] for x in data[-self.avg1:]]) > np.mean([x[4] for x in data[-self.avg2:]]):
            return True
        else:
            return False


run_PricePredictionAlgorithms = PricePredictionAlgorithms()
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

    global time_update, time_update_stop, list_all_available_crypto_euro, list_all_available_crypto_usdt, \
        list_crypto_to_live_price_alert, dct_break_point

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
    elif text[:3] == "add":
        name_index_char = text.index(" ")
        name = text[name_index_char + 1:]
        name = name.upper()

        if name in list_all_available_crypto_euro or name in list_all_available_crypto_usdt:
            list_crypto_to_live_price_alert.append(name)
            update.message.reply_text(
                f"{name} has been added to the live price.")
        else:
            update.message.reply_text(
                "Check that the given name is correct.")
    elif text[:6] == "remove":
        name_index_char = text.index(" ")
        name = text[name_index_char + 1:]
        name = name.upper()

        if name in list_crypto_to_live_price_alert:
            list_crypto_to_live_price_alert.remove(name)
            update.message.reply_text(f"{name} has been removed")
        else:
            update.message.reply_text(
                "The given name is not on the list! Make sure you enter the cryptocurrency name correctly.")
    # section responsible for break point
    elif text[:5] == "break":
        if text[6:8] == "up":
            name_price = text[9:]
            index_of_space = name_price.index(" ")
            name = name_price[:index_of_space].upper()
            check_if_exists = public_client.get_product_ticker(name)
            try:
                if check_if_exists["message"] == "NotFound":
                    update.message.reply_text("Error! Make sure you entered the correct name.")
                    return
            except KeyError:
                pass
            price = name_price[index_of_space + 1:]

            dct_break_point.update({name: {"up": price, "notify": False}})
        elif text[6:10] == "down":
            name_price = text[11:]
            index_of_space = name_price.index(" ")
            name = name_price[:index_of_space].upper()
            check_if_exists = public_client.get_product_ticker(name)
            try:
                if check_if_exists["message"] == "NotFound":
                    update.message.reply_text("Error! Make sure you entered the correct name.")
                    return
            except KeyError:
                pass
            price = name_price[index_of_space + 1:]

            dct_break_point.update({name: {"down": price, "notify": False}})
        else:
            update.message.reply_text("Error! Make sure you entered the correct message.")
    # script section
    elif text[:6] == "script":
        command = text
        index_of_equal = command.index("=")

        command_guess = command[index_of_equal + 1:]
        if command_guess == "help":
            update.message.reply_text(
                "The command is responsible for running an algorithm that examines the prices of "
                "cryptocurrencies (analyzes them)")
            update.message.reply_text("Example use of the command: script=1 BTC-USD")
            update.message.reply_text("Example use of the command: script=1 -a")
            update.message.reply_text("If you want to know what a certain script does, use the command: script=1 -h")
            update.message.reply_text("If you need extended help, type: script=all-help")
            return

        result = run_PricePredictionAlgorithms.main(command_guess)
        if result is not None:
            update.message.reply_text(result)


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
