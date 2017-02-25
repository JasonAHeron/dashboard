from flask import Flask, request, render_template
from datetime import datetime
from models import DeviceConnection
from google.appengine.api import users

app = Flask(__name__)
app.config['DEBUG'] = True

DEVICE_OWNERS = {
    'android-d8973f71e80d2c9b': 'Jason',
    'Michaels-iPhone': 'Michael',
    'jheron-macbookpro': 'Jason',
    'Chromecast': 'House',
    'Jasons-Air': 'Jason',
    'Michaels-MBP': 'Michael',
    'raspberrypi': 'House',
    '0005CD626483': 'House',
}
PHONES = ['android-d8973f71e80d2c9b', 'Michaels-iPhone']
VALID_USERS = ['jasonaheron@gmail.com', 'michael@stewart.io', 'arlingtondashboard@gmail.com']


class Device(object):
    """A device on the network."""

    def __init__(self, device_connection, current_time=datetime.now()):
        self.last_seen = current_time - device_connection.time
        self.name = device_connection.device_name

    @property
    def is_home(self):
        return self.last_seen.seconds / 60 <= 2

    @property
    def last_seen_minutes(self):
        return (self.last_seen.seconds % 3600) / 60

    @property
    def last_seen_hours(self):
        return self.last_seen.seconds / 3600

    @property
    def is_phone(self):
        return self.name in PHONES


class Owner(object):
    """An owner of one or more devices on the network."""

    def __init__(self, name, current_time=datetime.now()):
        self.devices = []
        self.name = name
        self.current_time = current_time

    def add_device(self, device_connection):
        self.devices.append(Device(device_connection, self.current_time))

    @property
    def is_home(self):
        return bool([device for device in self.devices if device.is_home and device.is_phone])


@app.route('/')
def homepage():
    """Return the dashboard homepage."""
    user = users.get_current_user()
    if not user or user.email().lower() not in VALID_USERS:
        login_url = users.create_login_url('/')
        return render_template('home.html', login_url=login_url)

    device_connections = DeviceConnection.query()
    now = datetime.now()
    owners = {}

    for device_connection in device_connections:
        owner_name = DEVICE_OWNERS.get(device_connection.device_name, 'Other')
        if owners.get(owner_name):
            owners[owner_name].add_device(device_connection)
        else:
            owners[owner_name] = Owner(owner_name, now)
            owners[owner_name].add_device(device_connection)

    owners_to_display = []
    owners_to_display.append(owners.get('Jason'))
    owners_to_display.append(owners.get('Michael'))
    owners_to_display.append(owners.get('Other'))

    return render_template('home.html', logged_in=True, data=[owner for owner in owners_to_display if owner is not None])


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
