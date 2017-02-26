"""Arlington Dashboard."""
from constants import VALID_USERS, DEVICE_OWNERS, BACKGROUNDS
from datetime import datetime
from flask import Flask, request, render_template, redirect
from google.appengine.api import users, memcache
from models import DeviceConnection, Owner
from utils import KeyDefaultDict
import random

app = Flask(__name__)
app.config['DEBUG'] = True
ONE_DAY = 86400


@app.route('/')
def homepage():
    """Return the dashboard homepage."""
    user = users.get_current_user()
    if not user or user.email().lower() not in VALID_USERS:
        login_url = users.create_login_url('/')
        return redirect(login_url, code=302)

    owners = KeyDefaultDict(Owner)
    owners.set_now(datetime.now())
    [
        owners[DEVICE_OWNERS.get(device.device_name, 'Other')].add_device(device)
        for device in DeviceConnection.query()
    ]
    owners_to_display = [
        owners.get('Jason'),
        owners.get('Michael'),
        owners.get('Other')
    ]

    backgroud = memcache.get(key='background')
    if not backgroud:
        backgroud = random.choice(BACKGROUNDS)
        memcache.add(key='background', value=backgroud, time=ONE_DAY)

    return render_template(
        'home.html',
        backgroud=backgroud,
        data=[owner for owner in owners_to_display if owner is not None]
    )


@app.route('/arp')
def update_devices():
    """Update datastore with current device last seen times."""
    devices = request.args.get('value')
    if devices:
        for device in devices.split('\n'):
            key = DeviceConnection.find(device)
            if key:
                DeviceConnection.update_time(key[0])
            else:
                DeviceConnection.create(device)
    return 'Updated {}'.format(devices.split('\n') if devices else 'NONE')


@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, nothing at this URL.', 404
