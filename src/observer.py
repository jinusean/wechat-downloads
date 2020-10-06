from copy import deepcopy

class ObservableDict:
    _observable = None
    _observers = None

    def __init__(self, observable):
        observable = deepcopy(observable)
        self._observable = self._build_observable(observable)
        self._observers = {}

    def _build_observable(self, obj):
        observable = {}

        for key, value in obj.items():
            if key in ObservableDict.__dict__:
                print('Warning: class and object both has key: ' + key)
            if isinstance(value, dict):
                value = ObservableDict(value)
            observable[key] = value

        return observable

    def __getitem__(self, key):
        return object.__getattribute__(self, '_observable')[key]

    def __setitem__(self, key, new_value):
        old_value = self._observable.get(key)

        if key not in self._observers:
            self._observers[key] = {}

        for observer in self._observers[key].values():
            observer(old_value, new_value)

        self._observable[key] = new_value



    def __delattr__(self, key):
        if key not in self._observable:
            return

        old_value = self._observable.get(key)
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

