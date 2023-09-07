import badger2040
import time
import machine
import pcf85063a
import urequests

display : badger2040.Badger2040 = None # type: ignore

WIDTH = 296
HEIGHT = 128
LOOP_SLEEP_SECONDS=60
TIME_OFFSET = 10 * 60 * 60
FONT_SIZE = 2
IS_DARK_MODE = False


def get_display():
    global display
    if display is None:
        display = badger2040.Badger2040()
    return display