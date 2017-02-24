from google.appengine.ext import ndb
from flask import Flask, request, render_template
from datetime import datetime
app = Flask(__name__)
app.config['DEBUG'] = True

# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.


class DeviceConnection(ndb.Model):
    device_name = ndb.StringProperty()
    time = ndb.DateTimeProperty(auto_now=True)

    @classmethod
    def create(cls, device_name):
        connection = cls(device_name=device_name)
        connection.put()
        return connection

    @classmethod
    def update_time(cls, key):
        key.put()

    @classmethod
    def find(cls, device_name):
        return cls.query(cls.device_name == device_name).fetch(1)


@app.route('/')
def hello():
    """Return a friendly HTTP greeting."""
    device_connections = DeviceConnection.query()
    now = datetime.now()
    return render_template('home.html', data={connection.device_name: now - connection.time for connection in device_connections})


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
