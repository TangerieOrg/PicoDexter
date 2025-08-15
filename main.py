
# import WIFI_CONFIG
# WIFI_CONFIG.configure()
try:
    import display, badger2040, uasyncio, usys
    badger2040.reset_pressed_to_wake() 
    if display.display.pressed(badger2040.BUTTON_A):
        display.clear(True) 
        display.text_center("Exit", 5, 70)
        display.update()
    else:
        import blue
        uasyncio.run(blue.main())
except Exception as e:
    import usys, uio, util, badger2040
    import display

    WIDTH, HEIGHT = display.display.get_bounds()
    FONT_SIZE = 2

    display.display.set_font("bitmap8")
    display.display.set_update_speed(badger2040.UPDATE_MEDIUM)

    buff = uio.StringIO()
    usys.print_exception(e, buff) # type: ignore

    display.display.set_pen(15)
    display.display.clear()
    display.display.set_pen(0)
    display.display.text(type(e).__name__, 20, 10, WIDTH - 40, 3)
    for i, line in enumerate(buff.getvalue().split("\n")):
        display.display.text(line, 20, int(40 + i * 9 * 1.3), WIDTH - 40, 1.3)
    display.update()
    usys.print_exception(e)
    usys.exit(1)
