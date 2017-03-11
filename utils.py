"""Some utils to make the app a bit cleaner."""
from collections import defaultdict
from constants import VALID_USERS, DEVICE_OWNERS
from datetime import datetime
from flask import redirect
from functools import wraps
from google.appengine.api import users
from models import Owner, DeviceConnection


class KeyDefaultDict(defaultdict):
    """This is the API I wish defaultdict had."""

    def __missing__(self, key):
        """Just ignore this hack."""
        if self.default_factory is None:
            raise KeyError(key)
        else:
            ret = self[key] = self.default_factory(key, self.now)
            return ret

    def set_now(self, now):
        """Also a hack."""
        self.now = now


def login_required(f):
    """Allow us to limit access in a DRY way."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = users.get_current_user()
        if not user or user.email().lower() not in VALID_USERS:
            return redirect(users.create_login_url('/'), code=302)
        return f(*args, **kwargs)
    return decorated_function


def create_owners_dict():
    """Create a mapping from owners to devices."""
    owners = KeyDefaultDict(Owner)
    owners.set_now(datetime.now())
    [
        owners[DEVICE_OWNERS.get(device.device_name, 'Other')].add_device(device)
        for device in DeviceConnection.query()
    ]
    return owners
