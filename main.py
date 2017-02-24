from flask import Flask, request, render_template
from datetime import datetime
from models import DeviceConnection
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


@app.route('/')
def homepage():
    """Return the dashboard homepage."""
    device_connections = DeviceConnection.query()
    now = datetime.now()
    return render_template('home.html', data=[DeviceInfo(connection, now) for connection in device_connections])


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
    return 'Updated {}'.format(devices.split('\n'))


@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, nothing at this URL.', 404
