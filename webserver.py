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
	# oldtime = shared['oldtime']
	# overridden = shared['overridden']
	# override_time = time.strftime("%x %X", time.localtime(shared['override_time']))
	# time_to_siren = time.strftime("%H:%M:%S", time.gmtime(abs(shared['seconds'] - (time.time() - oldtime))))
	# if shared['overridden']:
	# 	time_to_unoverride = time.strftime("%H:%M:%S", time.gmtime(abs(shared['delay'] - (time.time() - shared['override_time']))))
	# else:
	# 	time_to_unoverride = "00:00:00"
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
		"overridden": 0,
		"override_time": 0,
		"short_overriders": short_overriders,
		"long_overriders": long_overriders,
		"time": 0,
		"otime": 0,
		"delay": DELAY.DEFAULT(),
		"temperature": temperature
	}

	return json.dumps(data)


@app.route('/update', methods=["POST"])
def update():
	global default_delay, short_overriders, long_overriders

	if request.form["password"] != "password":
		return "incorrect password"
	if request.form["delay"].isnumeric() or request.form["short_overriders"] or request.form['long_overriders']:
		default_delay = int(request.form['delay'])
		door_btn.hold_time = default_delay
		with open("./settings/delay.txt", "w") as f:
			f.write(str(request.form['delay']))
			f.close()

		short_overriders = [x.strip() for x in request.form['short_overriders'].split(",")]
		with open("./settings/short_overriders.txt", "w") as f:
			f.write(str(request.form['short_overriders']))
			f.close()

		long_overriders = [x.strip() for x in request.form['long_overriders'].split(",")]
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