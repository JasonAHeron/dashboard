"""Data models for the app."""
from google.appengine.ext import ndb
from constants import PHONES


"""Database models."""


class DeviceConnection(ndb.Model):
    """A record of a device connected to the network."""

    device_name = ndb.StringProperty()
    time = ndb.DateTimeProperty(auto_now=True)

    @classmethod
    def create(cls, device_name):
        """Create a connection object."""
        connection = cls(device_name=device_name)
        connection.put()
        return connection

    @classmethod
    def update_time(cls, key):
        """Update the time of an existing connection to NOW."""
        key.put()

    @classmethod
    def find(cls, device_name):
        """Get a connection object by device name."""
        return cls.query(cls.device_name == device_name).fetch(1)


class RouterSecret(ndb.Model):
    """Why can't we store env variables via app engine webUI."""

    secret = ndb.StringProperty()

    @classmethod
    def value(cls):
        """Shortcut to get the string value."""
        return cls.query().fetch()[0].secret


"""Python Models."""


class Device(object):
    """A device on the network."""

    def __init__(self, device_connection, current_time):
        """Create a new device."""
        self.last_seen = current_time - device_connection.time
        self.name = device_connection.device_name

    @property
    def last_seen_days(self):
        """Number of days since the device was last seen."""
        return self.last_seen.days

    @property
    def is_home(self):
        """If the device is currently on the network."""
        return self.last_seen.seconds / 60 <= 2 and self.last_seen.days == 0

    @property
    def last_seen_minutes(self):
        """Number of minutes since the device was last seen % hours."""
        return (self.last_seen.seconds % 3600) / 60

    @property
    def last_seen_hours(self):
        """Number of hours since the device was last seen % days."""
        return self.last_seen.seconds / 3600

    @property
    def is_phone(self):
        """If the device is a phone."""
        return self.name in PHONES


class Owner(object):
    """An owner of one or more devices on the network."""

    def __init__(self, name, current_time):
        """Create a new owner."""
        self.devices = []
        self.name = name
        self.current_time = current_time

    def add_device(self, device_connection):
        """Add a device object to be owned by this owner."""
        self.devices.append(Device(device_connection, self.current_time))

    @property
    def is_home(self):
        """If the device owner is currently on the network."""
        return bool([
            device for device in self.devices
            if device.is_home and device.is_phone
        ])
