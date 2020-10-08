from copy import deepcopy


class ObservableDict:
    _observable = None
    _observers = None

    def __init__(self, _dict):
        self._observable = self._build_observable(_dict)
        self._observers = {}
        self._all_observer = {}  # observer of all keys

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
        old_value = self._observable[key]

        # create observer.dict
        if key not in self._observers:
            self._observers[key] = {}

        self._observable[key] = new_value

        for observer in self._observers[key].values():
            observer(old_value, new_value)

        for observer in self._all_observer.values():
            observer(key, old_value, new_value)

    def __delitem__(self, key):
        old_value = self._observable[key]
        for observer in self._observers[key].values():
            observer(old_value, None)

        del self._observable[key]
        del self._observers[key]

    def watch(self, key, fn):
        """
        Watch key for changes. If key=None the passed fn will be called for every change
        :param key: dict[key] to watch
        :param fn: on change handler
        """
        # lazy set key observer
        if key and key not in self._observers:
            self._observers[key] = {}

        assert callable(fn)
        if key:
            self._observers[key][fn] = fn
        else:
            self._all_observer[fn] = fn


    def unwatch(self, key, fn):
        if key:
            del self._observers[key][fn]
        else:
            del self._all_observer[fn]

    def clear(self, key):
        """
        Clears all observers for a key
        :param key:
        """
        del self._observers[key]

    def clear_all(self):
        self._observers = {}
        self._all_observer = {}
