import badger2040
import util
import time
import machine
import pcf85063a
import urequests
import ntptime
import random
import network

from display import *

network.hostname("PicoDexter")
network.country("TH")


def rjust(text, length : int, fill : str):
    text = str(text)
    if len(text) >= length: return text
    else: return fill * (length - len(text)) + text

def ljust(text, length : int, fill : str):
    text = str(text)
    if len(text) >= length: return text
    else: return text + fill * (length - len(text))

def dateToStr(d : tuple[int, int, int, int, int, int, int, int]):
    year, month, day, hour, minute, second, dow, doy = d
    return f"{hour}:{minute}:{second} {day}/{month}/{year}"

# for i, ap in enumerate(scan_aps()):
#     display.text(ap, 10, 45 + i * 15, scale=1.5)
clear()
display.update()

display.set_update_speed(badger2040.UPDATE_TURBO)

i2c = machine.I2C(0)
rtc = pcf85063a.PCF85063A(i2c) # type: ignore
i2c.writeto_mem(0x51, 0x00, b'\x00')  # ensure rtc is running (this should be default?)
rtc.enable_timer_interrupt(False)
rtc.clear_alarm_flag()

was_connected = display.get_network_manager().isconnected()
if not was_connected:
    progress_bar(4, 0)    
    display.text("WiFi", 10, 10, 256, 4)
    import WIFI_CONFIG
    display.text(f"SSID = {WIFI_CONFIG.SSID}", 10, config.HEIGHT // 2 + 15 + 5, scale=2)
    display.update()

    display.connect(status_handler=None)  # type: ignore

    progress_bar(4, 1/3)
    display.text("IP = " + str(display.ip_address()), 10, config.HEIGHT // 2 + 45, scale=2)
    display.update()

    time.sleep(2)

    clear()
    progress_bar(4, 2 / 3) 
    display.text("Clock", 10, 10, 256, 4)
    display.update()

    try:
        ntptime.settime()
        badger2040.pico_rtc_to_pcf() #type: ignore
    except: pass    

    progress_bar(4, 1)
    display.text(dateToStr(time.localtime(time.time() + TIME_OFFSET)), 10, HEIGHT // 2 + 45, scale=2) # type: ignore
    display.update()
    time.sleep(2)

print("[BOOT] Finished")
display.set_update_speed(badger2040.UPDATE_FAST)


def wait_loop():
    year, month, day, hour, minute, second, dow = rtc.datetime()
    sec_since_epoch = time.mktime((year, month, day, hour, minute, second, dow, 0)) + config.LOOP_SLEEP_SECONDS + random.randint(-5, 5)

    (ayear, amonth, aday, ahour, aminute, asecond, adow, adoy) = time.localtime(sec_since_epoch)

    rtc.clear_alarm_flag()
    rtc.set_alarm(asecond, aminute, ahour, aday)
    rtc.enable_alarm_interrupt(True)


def text_center(text, size : float, y : int, fixed_width = False):
    text = str(text)
    w = display.measure_text(text, size, fixed_width=fixed_width)
    display.text(text, int(config.WIDTH / 2 - w / 2), y, config.WIDTH, size, fixed_width=fixed_width)
    return w



def format_time(date : tuple[int, int, int, int, int, int, int, int]) -> str:
    hour = date[3] % 12
    if hour == 0: hour = 12
    minute = date[4]

    return f"{rjust(hour, 2, '0')}:{rjust(minute, 2, '0')} {'PM' if date[3] >= 12 else 'AM'}"

last_run = 0
last_value = 0

def update_time(seconds_since, do_update=True):
    clear()
    text_center(f"{rjust(seconds_since // 60, 2, '0')}m {rjust(seconds_since % 60, 2, '0')}s", 2, 105)

def run(force_update=False):
    global last_run, last_value

    if last_value == 0:
        readings = urequests.get("http://tangerie.xyz/dexter/api/glucose/ten").json()
        prev = readings[-2]
        last_value = prev["value"]
        last_run = readings[-1]["date"]


    data = urequests.get("http://tangerie.xyz/dexter/api/glucose/current").json()

    trend : str = data["trend"]
    value : float = data["value"]
    date = time.localtime(int(data["date"] / 1000.0) + config.TIME_OFFSET)

    display.set_update_speed(badger2040.UPDATE_TURBO)

    has_changed = last_run != data["date"]

    if not has_changed and not force_update:
        display.set_update_speed(badger2040.UPDATE_TURBO)
    else:
        display.set_update_speed(badger2040.UPDATE_MEDIUM)
    
    update_time(time.time() - last_run // 1000, False)
    
    last_run = data["date"]
    v_w = text_center(value, 5, 10)
    display.text("mmol/L", int(config.WIDTH / 2 + v_w / 2) + 5, 30, config.WIDTH, 2)
    diff = value - last_value
    if last_value == 0:
        diff = 0
    # text_center(trend, 2.5, 80)
    text_center(f"{trend} ({'+' if diff >= 0 else ''}{round(diff, 2)})", 2.5, 70)

    # text_center(format_time(date), 2, 95) # type: ignore
    if has_changed:
        last_value = value
    display.update()


while True:
    display.keepalive()
    run(force_update=display.pressed(badger2040.BUTTON_DOWN) or display.pressed(badger2040.BUTTON_B))
    break
    wait_loop()
    display.halt()


    
