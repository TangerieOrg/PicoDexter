import badger2040
import util
import display
import asyncio
import aioble
import time
import bluetooth
from ble_simple_peripheral import BLESimplePeripheral

async def display_loop(task):
    display.display.set_update_speed(badger2040.UPDATE_FAST)
    counter = 0
    while not display.display.pressed_any():
        display.clear()
        display.progress_bar(4, (counter % 5) / 4)
        display.update()
        counter += 1
        await asyncio.sleep_ms(100)
    task.cancel()

async def main():
    display.clear(True)
    display.update()
    ble = bluetooth.BLE()
    p = BLESimplePeripheral(ble, "Dexter")
    
    def on_rx(v):
        print("RX", v)

    p.on_write(on_rx)
    
    advertise_task = asyncio.create_task(p.advertise())
    display_task = asyncio.create_task(display_loop(advertise_task))
    
    await advertise_task
    
    display_task.cancel()
    
    display.clear()
    display.text_center("Connected", 5, 25)
    display.text_center(str(p.is_connected()), 5, 70)
    display.update()

    
    p.disconnect()