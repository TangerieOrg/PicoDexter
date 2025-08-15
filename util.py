import badger2040
from picographics import PicoGraphics, DISPLAY_INKY_PACK
import asyncio

display : badger2040.Badger2040 = None # type: ignore


def get_display():
    global display
    if display is None:
        display = badger2040.Badger2040()
        
    return display

def rotate_display(rotation : int):
    d = get_display()
    d.display = PicoGraphics(DISPLAY_INKY_PACK, rotate=rotation)
    return d
