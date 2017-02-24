from google.appengine.ext import ndb


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
