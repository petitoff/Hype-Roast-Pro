from core import *

# Starting auxiliary functions
get_list_of_all_crypto_to_euro()

# telegram bot and sending message (all api and other main def)
thread1 = Thread(target=telegram_main)

thread1.setDaemon(True)
thread1.start()
try:
    while True:
        pass
except KeyboardInterrupt:
    pass
