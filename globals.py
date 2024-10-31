from gpiozero import Device, LED, Button
from gpiozero.mixins import HoldThread
from gpiozero.pins.mock import MockFactory

Device.pin_factory = MockFactory()

default_delay = int(open('settings/delay.txt', 'r').read())

class DELAY:
    DEFAULT = lambda : default_delay
    SHORT = lambda : 2
    LONG = lambda : 5


door_btn = Button(17, hold_time=DELAY.DEFAULT(), pull_up=False)
button_btn = Button(1, pull_up=True)
unlock_led = LED(16)
beep_led = LED(23)
siren_led = LED(26)

short_overriders = open('settings/short_overriders.txt', 'r').read()
long_overriders = open('settings/long_overriders.txt', 'r').read()

def siren_on():
    door_btn.hold_time = DELAY.DEFAULT()
    siren_led.on()

def siren_off(temporary = None):
    if temporary:
        if not siren_led.is_active:
            return False
        door_btn.hold_time = temporary()
        door_btn._fire_activated()
    siren_led.off()
    return True

def unlock_door(seconds):
    if unlock_led.is_active:
        return False
    unlock_led.blink(seconds, 1, 1)
    return True

def play_beep(t):
    if t == 'good':
        beep_led.blink(0.125, 0.125, 2)
    elif t == 'bad':
        beep_led.blink(0.002, 0.002, 200)
    elif isinstance(t, int):
        beep_led.blink(t, 0, 1)
