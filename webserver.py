from flask import Flask, render_template, request, send_from_directory
import json
from globals import *
import logging

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
	return render_template("index.html")


@app.route('/log', methods=['GET'])
def sendlog():
	return send_from_directory('logs', 'log.txt')


@app.route('/status', methods=['GET'])
def status():
	temperature = 0
	try:
		with open('/sys/class/thermal/thermal_zone0/temp') as f:
			temperature = round(float(f.read())/1000)
	except:
		None

	data = {
		"door": door_btn.is_active,
		"door_lock": unlock_led.is_active,
		"siren": siren_led.is_active,
		"button": button_btn.is_active,
		"short_overriders": OVERRIDERS.SHORT,
		"long_overriders": OVERRIDERS.LONG,
		"siren_time": TIMES.SIREN(),
		"door_time": TIMES.DOOR(),
		"default_delay": DELAY.DEFAULT,
		"short_delay": DELAY.SHORT,
		"long_delay": DELAY.LONG,
		"temperature": temperature
	}

	return json.dumps(data)


@app.route('/update', methods=["POST"])
def update():
	import globals

	if request.form["password"] != "password":
		return "incorrect password"
	if request.form["default_delay"].isnumeric() or request.form["short_delay"].isnumeric() or request.form["long_delay"].isnumeric() or request.form["short_overriders"] or request.form['long_overriders']:
		globals.DELAY.DEFAULT = int(request.form['default_delay'])
		door_btn.hold_time = globals.DELAY.DEFAULT
		with open("settings/default_delay.txt", "w") as f:
			f.write(str(request.form['default_delay']))
			f.close()

		globals.DELAY.SHORT = int(request.form['short_delay'])
		with open("settings/short_delay.txt", "w") as f:
			f.write(str(request.form['short_delay']))
			f.close()

		globals.DELAY.LONG = int(request.form['long_delay'])
		with open("settings/long_delay.txt", "w") as f:
			f.write(str(request.form['long_delay']))
			f.close()

		globals.OVERRIDERS.SHORT = [x.strip() for x in request.form['short_overriders'].split(",")]
		with open("./settings/short_overriders.txt", "w") as f:
			f.write(str(request.form['short_overriders']))
			f.close()

		globals.OVERRIDERS.LONG = [x.strip() for x in request.form['long_overriders'].split(",")]
		with open("./settings/long_overriders.txt", "w") as f:
			f.write(str(request.form['long_overriders']))
			f.close()

		return "updated"
	else:
		return "bad form"


@app.route('/unlock', methods=["POST"])
def unlock():
	if not unlock_door(30):
		return "already unlocked"
	else:
		return "unlocked"


@app.route('/override', methods=["POST"])
def override():
	if request.form["password"] != "password":
		return "incorrect password"

	if not siren_off(temporary=DELAY.LONG):
		return "siren is not activated"
	else:
		return "overridden"