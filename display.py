import badger2040
import config
import util


display = util.get_display()
util.rotate_display(180 if not display.pressed(badger2040.BUTTON_DOWN) else 0)
display.set_font("bitmap8")
display.set_update_speed(badger2040.UPDATE_MEDIUM)

def set_pen(level : int):
    display.set_pen((15 - level) if config.IS_DARK_MODE else level)

def foreground(): set_pen(0)
def background(): set_pen(15)

def clear(_update=False):
    background()
    display.clear()
    foreground()
    if _update: update()
    
def progress_bar(thickness, perc):
    foreground()
    display.rectangle(5, config.HEIGHT // 2 - 15, config.WIDTH - 10, 30)
    background()
    max_w = config.WIDTH - 10 - thickness * 2
    offX = int(perc * max_w)
    display.rectangle(
        5 + thickness + offX, 
        config.HEIGHT // 2 - 15 + thickness, 
        config.WIDTH - 10 - thickness * 2 - offX, 
        30 - thickness * 2
    )
    foreground()
    
def update():
    return display.update()

def text_center(text, size : float, y : int, fixed_width = False):
    text = str(text)
    w = display.measure_text(text, size, fixed_width=fixed_width)
    display.text(text, int(config.WIDTH / 2 - w / 2), y, config.WIDTH, size, fixed_width=fixed_width)
    return w