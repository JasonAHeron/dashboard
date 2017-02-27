"""Arlington Dashboard."""
from constants import BACKGROUNDS
from flask import Flask, request, render_template, redirect
from google.appengine.api import users
from models import DeviceConnection
from utils import user_is_not_authenticated, create_owners_dict
import random

app = Flask(__name__)
app.config['DEBUG'] = True


@app.route('/background')
def background():
    """Return the background URL."""
    if user_is_not_authenticated():
        return redirect(users.create_login_url('/'), code=302)
    return random.choice(BACKGROUNDS)


@app.route('/whoishome')
def whoishome():
    """Return the home status cards."""
    if user_is_not_authenticated():
        return redirect(users.create_login_url('/'), code=302)
    owners = create_owners_dict()
    owners_to_display = [
        owners.get('Jason'),
        owners.get('Michael'),
        owners.get('Other')
    ]
    return render_template(
        'whoishome.html',
        data=[
            owner for owner in owners_to_display
            if owner is not None
        ]
    )


@app.route('/')
def homepage():
    """Return the dashboard homepage."""
    if user_is_not_authenticated():
        return redirect(users.create_login_url('/'), code=302)
    return render_template('home.html')


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
