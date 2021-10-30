from core import *

# Starting auxiliary functions
get_list_of_all_crypto_to_euro()
get_list_of_all_crypto_to_tether()
get_list_of_all_crypto_to_usd()

# telegram bot and sending message (all api and other main def)
thread1 = Thread(target=telegram_main)
thread2 = Thread(target=live_price_cryptocurrency)
thread3 = Thread(target=break_point)

thread1.setDaemon(True)
thread1.start()

thread2.setDaemon(True)
thread2.start()

thread3.setDaemon(True)
thread3.start()

run_BigDifferencesInPrices = BigDifferencesInPrices()
thread1_1 = Thread(target=run_BigDifferencesInPrices.main_function)
thread1_1.setDaemon(True)
thread1_1.start()

run_PricePredictionAlgorithms = PricePredictionAlgorithms()
thread1_2 = Thread(target=run_PricePredictionAlgorithms.main)
thread1_2.setDaemon(True)
thread1_2.start()

try:
    while True:
        pass
except KeyboardInterrupt:
    pass
