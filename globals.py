from gpiozero import Device, LED, Button
from gpiozero.pins.mock import MockFactory
import sys
import time

if sys.platform.startswith("win"):
    Device.pin_factory = MockFactory()

class DelaysClass:
    def __init__(self):
        self.DEFAULT = int(open('settings/default_delay.txt', 'r').read())
        self.SHORT = int(open('settings/short_delay.txt', 'r').read())
        self.LONG = int(open('settings/long_delay.txt', 'r').read())

DELAY = DelaysClass()

door_btn = Button(17, hold_time=DELAY.DEFAULT, pull_up=True)
button_btn = Button(12, pull_up=True)
unlock_led = LED(16)
beep_led = LED(23)
siren_led = LED(26)

wiegand_white = 9
wiegand_green = 11

class OverridersClass:
    def __init__(self):
        self.SHORT = open('settings/short_overriders.txt', 'r').read()
        self.LONG = open('settings/long_overriders.txt', 'r').read()

OVERRIDERS = OverridersClass()

siren_time = None
door_opened_time = None

class TIMES:
    SIREN = lambda : hms(int(time.time() - siren_time)) if siren_time is not None else (hms(-(door_btn.hold_time - (time.time() - door_opened_time))) if door_opened_time is not None else None)
    DOOR = lambda : hms(int(door_btn.active_time)) if door_btn.active_time else 0

def siren_on():
    global siren_time
    door_btn.hold_time = DELAY.DEFAULT
    siren_led.on()
    siren_time = time.time()

def siren_off(temporary = None):
    global siren_time, door_opened_time
    if temporary:
        if not siren_led.is_active:
            return False
        door_btn.hold_time = temporary
        door_btn._fire_activated()
    siren_led.off()
    siren_time = None
    door_opened_time = None
    return True

def unlock_door(seconds):
    if unlock_led.is_active:
        return False
    unlock_led.blink(seconds, 1, 1)
    return True

def door_opened():
    global door_opened_time
    door_opened_time = time.time()

def play_beep(t):
    if t == 'good':
        beep_led.blink(0.125, 0.125, 2)
    elif t == 'bad':
        beep_led.blink(0.002, 0.002, 200)
    elif isinstance(t, int):
        beep_led.blink(t, 0, 1)

def hms(i):
    i = int(i)
    sign = ''
    if i < 0:
        sign = '-'
        i *= -1
    i %= 86400
    return sign + time.strftime('%H:%M:%S', time.gmtime(i))