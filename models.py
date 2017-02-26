from google.appengine.ext import ndb
from constants import PHONES

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


class Device(object):
    """A device on the network."""

    def __init__(self, device_connection, current_time):
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

    def __init__(self, name, current_time):
        self.devices = []
        self.name = name
        self.current_time = current_time

    def add_device(self, device_connection):
        self.devices.append(Device(device_connection, self.current_time))

    @property
    def is_home(self):
        return bool([
            device for device in self.devices
            if device.is_home and device.is_phone
        ])
