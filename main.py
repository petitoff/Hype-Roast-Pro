from core import *

# telegram bot and sending message (all api and other main def)
thread1 = Thread(target=telegram_main)

thread1.setDaemon(True)
thread1.start()
try:
    while True:
        pass
except KeyboardInterrupt:
    pass
