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

VALID_USERS = ['jasonaheron@gmail.com', 'michael@stewart.io']


class DeviceInfo(object):
    def __init__(self, device_connection, current_time=datetime.now()):
        self.last_seen = current_time - device_connection.time
        self.device_name = device_connection.device_name
        self.owner = DEVICE_OWNERS.get(self.device_name, 'Unknown')

    @property
    def is_home(self):
        return self.last_seen.seconds // 60 < 2

    @property
    def last_seen_minutes(self):
        return (self.last_seen.seconds % 3600) // 60

    @property
    def last_seen_hours(self):
        return self.last_seen.seconds // 3600


class DeviceOwner(object):
    def __init__(self, name, current_time=datetime.now()):
        self.devices = []
        self.name = name
        self.current_time = current_time

    def add_device(self, device_connection):
        self.devices.append(DeviceInfo(device_connection, self.current_time))

    @property
    def is_home(self):
        return bool([device for device in self.devices if device.is_home])


@app.route('/')
def homepage():
    """Return the dashboard homepage."""
    user = users.get_current_user()
    if not user or user.email().lower() not in VALID_USERS:
        login_url = users.create_login_url('/')
        return render_template('home.html', login_url=login_url)

    device_connections = DeviceConnection.query()
    now = datetime.now()

    owners = {
        'Jason': DeviceOwner('Jason', now),
        'Michael': DeviceOwner('Michael', now),
        'House': DeviceOwner('House', now),
        'Other': DeviceOwner('Other', now)
    }

    for device_connection in device_connections:
        owners[DEVICE_OWNERS.get(device_connection.device_name, 'Other')].add_device(device_connection)

    return render_template('home.html', user=user, data=[owners['Jason'], owners['Michael'], owners['House'], owners['Other']])


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
