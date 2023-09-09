while True:
    try:
        import program
    except Exception as e:
        import usys, io, util, badger2040
        display = util.get_display()

        WIDTH, HEIGHT = display.get_bounds()
        FONT_SIZE = 2

        display.set_font("bitmap8")
        display.set_update_speed(badger2040.UPDATE_MEDIUM)

        buff = io.StringIO()
        usys.print_exception(e, buff)
        display.set_pen(15)
        display.clear()
        display.set_pen(0)
        display.text(type(e).__name__, 20, 10, WIDTH - 40, 3)
        for i, line in enumerate(str(buff.getvalue()).split("\n")):
            display.text(line, 20, int(40 + i * 9 * 1.3), WIDTH - 40, 1.3)
        display.update()
        import gc
        gc.collect()
        import time
        time.sleep(5)
