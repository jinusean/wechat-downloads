from lib.Singleton import Singleton
import logging, json

class WatchersManager(metaclass=Singleton):
    def __init__(self, app, filename):
        self._app = app
        self._watchers = []
        self._sync_times = {}
        self._filename = filename
        self.load()

    @property
    def app(self):
        return self._app

    @property
    def sync_times(self):
        return self._sync_times

    @property
    def watchers(self):
        return self._watchers

    def load(self):
        syncs = None
        try:
            with self._app.open(self._filename) as f:
                syncs = json.load(f)
        except FileNotFoundError:
            logging.getLogger('SyncManager').info('sync-times.json not found in Application Support. Loading default instead.')
        except Exception as e:
            logging.getLogger('SyncManager').error('Error loading sync-times.json')
            logging.getLogger('SyncManager').error(e)

        if not syncs:
            syncs = {}

        self._sync_times = syncs

    def save(self):
        syncs = self.sync_times
        with self.app.open(self._filename, 'w') as f:
            json.dump(syncs, f)
        logging.getLogger('SyncManager').info('Saved ' + self._filename)

    def add(self, obj, dir):
        obj_id = id(obj)
        cls_name = obj.__class__.__name__

        self.watchers.append((cls_name, obj_id, dir))
        logging.getLogger(cls_name).info('Start: ' + dir)

        if cls_name == 'UserWatcher':
            sync_times = self.sync_times
            if dir not in sync_times:
                sync_times[dir] = 0



    def remove(self, obj, dir):
        obj_id = id(obj)
        cls_name = obj.__class__.__name__

        self.watchers.remove((cls_name, obj_id, dir))
        logging.getLogger(cls_name).info('Stop: ' + dir)

    def get_dirs_by_cls(self, cls_name):
        return [dir for (cls, obj_id, dir) in self.watchers if cls_name == cls]


class SyncManager(metaclass=Singleton):
    def __init__(self, app, filename):
        self._app = app
        self._filename = filename
        self._sync_times = None

        self.load()

    @property
    def app(self):
        return self._app

    @property
    def sync_times(self):
        return self._sync_times

    def __getitem__(self, item):
        return self.sync_times[item]

    def __setitem__(self, key, value):
        self.sync_times[key] = value

    def load(self):
        syncs = None
        try:
            with self._app.open(self._filename) as f:
                syncs = json.load(f)
        except FileNotFoundError:
            logging.getLogger('SyncManager').info('sync-times.json not found in Application Support. Loading default instead.')
        except Exception as e:
            logging.getLogger('SyncManager').error('Error loading sync-times.json')
            logging.getLogger('SyncManager').error(e)

        if not syncs:
            syncs = {}

        self._sync_times = syncs

    def save(self):
        syncs = self.sync_times
        with self.app.open(self._filename, 'w') as f:
            json.dump(syncs, f)
        logging.getLogger('SyncManager').info('Saved ' + self._filename)
