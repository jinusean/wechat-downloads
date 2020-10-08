from copy import deepcopy


class ObservableDict:
    _observable = None
    _observers = None

    def __init__(self, _dict):
        self._observable = self._build_observable(_dict)
        self._observers = {}

    def get_dict(self):
        target = {}

        for key, value in self._observable.items():
            if isinstance(value, ObservableDict):
                value = value.get_dict()
            target[key] = value

        return target

    @property
    def observable(self):
        return self._observable

    def _build_observable(self, obj):
        observable = {}

        for key, value in obj.items():
            if isinstance(value, dict):
                value = ObservableDict(value)
            else:
                value = deepcopy(value)
            observable[key] = value

        return observable

    def get(self, key):
        return self[key]

    def __getitem__(self, key):
        return object.__getattribute__(self, '_observable')[key]

    def __setitem__(self, key, new_value):
        old_value = self._observable.get(key)

        if key not in self._observers:
            self._observers[key] = {}

        for observer in self._observers[key].values():
            observer(old_value, new_value)

        self._observable[key] = new_value

    def __delitem__(self, key):
        old_value = self._observable[key]
        for observer in self._observers[key].values():
            observer(old_value, None)

        del self._observable[key]
        del self._observers[key]

    def watch(self, key, fn):
        if key not in self._observers:
            self._observers[key] = {}

        assert callable(fn)
        self._observers[key][fn] = fn

    def unwatch(self, key, fn):
        obvservers = self._observers[key]
        del obvservers[fn]

    def clear(self, key):
        del self._observers[key]
