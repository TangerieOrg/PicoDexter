import badger2040
import util
import time
import machine
import pcf85063a
import urequests
import ntptime
import random
import network

network.hostname("PicoDexter")
network.country("AU")

display = util.get_display()

WIDTH, HEIGHT = (296, 128)
FONT_SIZE = 2
IS_DARK_MODE = False
LOOP_SLEEP_SECONDS=60
TIME_OFFSET = 10 * 60 * 60

def set_pen(level : int):
    display.set_pen((15 - level) if IS_DARK_MODE else level)

def foreground(): set_pen(0)
def background(): set_pen(15)

def clear():
    background()
    display.clear()
    foreground()

# for i, ap in enumerate(scan_aps()):
#     display.text(ap, 10, 45 + i * 15, scale=1.5)
display.set_font("bitmap8")
display.set_update_speed(badger2040.UPDATE_MEDIUM)
clear()
display.update()

display.set_update_speed(badger2040.UPDATE_TURBO)

def progress_bar(thickness, perc):
    foreground()
    display.rectangle(5, HEIGHT // 2 - 15, WIDTH - 10, 30)
    background()
    max_w = WIDTH - 10 - thickness * 2
    offX = int(perc * max_w)
    display.rectangle(
        5 + thickness + offX, 
        HEIGHT // 2 - 15 + thickness, 
        WIDTH - 10 - thickness * 2 - offX, 
        30 - thickness * 2
    )
    foreground()

progress_bar(4, 1 / 3)    
display.text("WiFi", 10, 10, 256, 4)
from WIFI_CONFIG import SSID
display.text(SSID, 10, HEIGHT // 2 + 15 + 5, scale=2)
display.update()

display.connect(status_handler=None)  # type: ignore

clear()
progress_bar(4, 2 / 3) 
display.text("Clock", 10, 10, 256, 4)
display.update()

i2c = machine.I2C(0)
rtc = pcf85063a.PCF85063A(i2c) # type: ignore
i2c.writeto_mem(0x51, 0x00, b'\x00')  # ensure rtc is running (this should be default?)
rtc.enable_timer_interrupt(False)
rtc.clear_alarm_flag()

ntptime.settime()
badger2040.pico_rtc_to_pcf() #type: ignore

print("[BOOT] Finished")
clear()
progress_bar(4, 1)
display.update()
display.set_update_speed(badger2040.UPDATE_FAST)


def wait_loop():
    year, month, day, hour, minute, second, dow = rtc.datetime()
    sec_since_epoch = time.mktime((year, month, day, hour, minute, second, dow, 0)) + LOOP_SLEEP_SECONDS + random.randint(-5, 5)

    (ayear, amonth, aday, ahour, aminute, asecond, adow, adoy) = time.localtime(sec_since_epoch)

    rtc.clear_alarm_flag()
    rtc.set_alarm(asecond, aminute, ahour, aday)
    rtc.enable_alarm_interrupt(True)

def dateToStr(d : tuple[int, int, int, int, int, int, int, int]):
    year, month, day, hour, minute, second, dow, doy = d
    return f"{hour}:{minute}:{second} {day}/{month}/{year}"


def text_center(text, size : float, y : int, fixed_width = False):
    text = str(text)
    w = display.measure_text(text, size, fixed_width=fixed_width)
    display.text(text, int(WIDTH / 2 - w / 2), y, WIDTH, size, fixed_width=fixed_width)
    return w

def rjust(text, length : int, fill : str):
    text = str(text)
    if len(text) >= length: return text
    else: return fill * (length - len(text)) + text

def ljust(text, length : int, fill : str):
    text = str(text)
    if len(text) >= length: return text
    else: return text + fill * (length - len(text))

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
    max_width = display.measure_text("00m 00s", 2)
    if do_update:
        display.partial_update(WIDTH // 2 - max_width // 2, 104, max_width, 16)


def run():
    global last_run, last_value

    if last_value == 0:
        readings = urequests.get("http://tangerie.xyz/dexter/api/glucose/ten").json()
        prev = readings[-2]
        last_value = prev["value"]
        last_run = readings[-1]["date"] - 1 


    data = urequests.get("http://tangerie.xyz/dexter/api/glucose/current").json()

    trend : str = data["trend"]
    value : float = data["value"]
    date = time.localtime(int(data["date"] / 1000.0) + TIME_OFFSET)

    if last_run == data["date"]:
        print("Skipping Run")
        update_time(time.time() - last_run // 1000, True)
        return
    
    update_time(time.time() - last_run // 1000, False)
    

    last_run = data["date"]
    v_w = text_center(value, 5, 10)
    display.text("mmol/L", int(WIDTH / 2 + v_w / 2) + 5, 30, WIDTH, 2)
    diff = value - last_value
    if last_value == 0:
        diff = 0
    # text_center(trend, 2.5, 80)
    text_center(f"{trend} ({'+' if diff >= 0 else ''}{round(diff, 2)})", 2.5, 70)

    # text_center(format_time(date), 2, 95)

    last_value = value
    display.update()


while True:
    display.keepalive()
    run()
    wait_loop()
    display.halt()


    
