class MultiMap(object):
    def __init__(self, mapping, default=None):
        """Defines a mapping with multiple keys per value.
        
        mapping is a dict of: tuple(key, key, key...) => value
        """
        self.storage = dict()
        self.default = default
        
        for keys, value in mapping.iteritems():
            for key in keys:
                self.storage[key] = value

    def __getitem__(self, key):
        return self.storage.get(key, self.default)
