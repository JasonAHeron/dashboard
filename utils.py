from collections import defaultdict
from constants import VALID_USERS, DEVICE_OWNERS
from google.appengine.api import users
from datetime import datetime
from models import Owner, DeviceConnection


class KeyDefaultDict(defaultdict):
    """just pretend this class doesn't exist."""

    def __missing__(self, key):
        if self.default_factory is None:
            raise KeyError(key)
        else:
            ret = self[key] = self.default_factory(key, self.now)
            return ret

    def set_now(self, now):
        self.now = now


def user_is_not_authenticated():
    user = users.get_current_user()
    return not user or user.email().lower() not in VALID_USERS


def create_owners_dict():
    owners = KeyDefaultDict(Owner)
    owners.set_now(datetime.now())
    [
        owners[DEVICE_OWNERS.get(device.device_name, 'Other')].add_device(device)
        for device in DeviceConnection.query()
    ]
    return owners
