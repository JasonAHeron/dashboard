from collections import defaultdict


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
