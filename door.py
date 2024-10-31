from webserver import app
import threading
import sys
import wiegand
import pigpio
from globals import *

# When the door has been left open, activate the siren
door_btn.when_held = siren_on
# When the door closes, deactivate the siren
door_btn.when_deactivated = siren_off
# When pressing the physical button, disable the siren for DELAY.SHORT
button_btn.when_activated = lambda a : siren_off(temporary=DELAY.SHORT)

wiegand_white = 9
wiegand_green = 11


def wiegand_callback(bits, value, raw):
    print(bits, value, raw)
    card = str(int(raw[9:25], 2))
    print(int(raw[9:25], 2))

    if card not in short_overriders + long_overriders:
        play_beep("bad")
        return

    # If the door is open
    if not door_btn.is_active:
        # If the card is a short overrider
        if card in short_overriders:
            siren_off(DELAY.SHORT)
            play_beep("good")

        # If the card is a long overrider, override
        elif card in long_overriders:
            siren_off(DELAY.LONG)
            play_beep("good")

        # Otherwise, door has been unlocked once already or user is not authorized
        else:
            play_beep("bad")

    # If the door is locked, unlock
    if not unlock_led.is_active:
        # with open("logs/log.txt", "a") as logfile:
        #	logfile.write("%s override at %s\n" % (str(card), time.ctime(time.time())))

        unlock_door(30)
        print("ran async")

pi = pigpio.pi()
w = wiegand.decoder(pi, wiegand_white, wiegand_green, wiegand_callback)

print(sys.platform)

if sys.platform.startswith("win"):
    # Keyboard control functions (modified)
    print("activate keyboard version")
    import keyboard

    def key_pressed(key):
        if key.name in key_map and not key_map[key.name].is_active:
            print(f'active {key.name}')
            key_map[key.name].pin.drive_low()

    def key_released(key):
        if key.name in key_map:
            print(f'inactive {key.name}')
            key_map[key.name].pin.drive_high()

    key_map = {
        'a': door_btn,
        'b': button_btn
    }

    for key in key_map.keys():
        keyboard.on_press_key(key, key_pressed)
        keyboard.on_release_key(key, key_released)
    # End keyboard control

# Threading for Flask
def run_flask():
    app.run(debug=True, use_reloader=False, host="0.0.0.0", port=80)

# Create and start the Flask thread
flask_thread = threading.Thread(target=run_flask)
flask_thread.start()