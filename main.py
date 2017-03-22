"""Arlington Dashboard."""
from BART import BART
from collections import defaultdict
from constants import BACKGROUNDS, IMPORTANT_PEOPLE
from flask import Flask, request, render_template
from models import DeviceConnection, RouterSecret
from utils import login_required, create_owners_dict
import random

app = Flask(__name__)
app.config['DEBUG'] = True


@app.route('/bart')
@login_required
def bart_estimates():
    """Return BART status cards."""
    trains = defaultdict(list)
    [
        trains[train.departure.destination].append(str(train.minutes))
        for train in BART()['glen'].north
    ]
    return render_template('bart.html', trains=trains)


@app.route('/background')
@login_required
def background():
    """Return the background URL."""
    return random.choice(BACKGROUNDS)


@app.route('/whoishome')
@login_required
def who_is_home():
    """Return who is home status cards."""
    owners = create_owners_dict()
    important_owners = [
        owners.get(person) for person in IMPORTANT_PEOPLE
    ]
    return render_template(
        'whoishome.html',
        data=[
            owner for owner in important_owners
            if owner is not None
        ]
    )


@app.route('/')
@login_required
def homepage():
    """Return the dashboard homepage."""
    return render_template('home.html')


@app.route('/arp')
def update_devices():
    """Update datastore with current device last seen times."""
    devices = request.args.get('value')
    secret = request.args.get('secret')
    if devices and secret == RouterSecret.value():
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
