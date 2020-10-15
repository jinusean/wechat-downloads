from lib.Singleton import Singleton
import logging, json
import time
from lib import debounce
from src import utils

logger = logging.getLogger('WatchersManager')


class WatchersManager(metaclass=Singleton):
    def __init__(self, app, filename):
        self._app = app
        self._watchers = []
        self._sync_times = {}  # UserWatcher sync times
        self._filename = filename
        self.load()

        self.debounced_save = debounce(5)(self.save)

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
            logger.info(
                '{} not found in Application Support. Loading default instead.'.format(self._filename))
        except Exception as e:
            logger.error('Error loading {}'.format(self._filename))
            logger.error(e)

        if not syncs:
            syncs = {}

        self._sync_times = syncs

    def save(self):
        syncs = self.sync_times
        with self.app.open(self._filename, 'w') as f:
            json.dump(syncs, f)
        logger.info('Saved ' + self._filename)

    def add(self, obj, dir):
        obj_id = id(obj)
        cls_name = obj.__class__.__name__

        self.watchers.append((cls_name, obj_id, dir))
        logging.getLogger(cls_name).info('Start: ' + dir)

        if cls_name == 'UserWatcher':
            self.sync_dir(dir)

    def remove(self, obj, dir):
        obj_id = id(obj)
        cls_name = obj.__class__.__name__

        self.watchers.remove((cls_name, obj_id, dir))
        logging.getLogger(cls_name).info('Stop: ' + dir)

        if cls_name == 'UserWatcher':
            self.sync_times[dir] = time.time()
            self.debounced_save()

    def sync_dir(self, dir, all=False):
        start_time = self.sync_times.get(dir) or 0
        end_time = time.time()
        count = 0
        for file in utils.iter_files(dir):
            stat = file.stat()
            modified_time = stat.st_mtime
            if not all and (start_time > modified_time or modified_time > end_time or not utils.validate_file(file)):
                # if last synced happened after file modification
                # if app has started before file modification
                continue

            utils.copy_file(file)
            count += 1
        logger.info("Synced {} files in {}".format(count, dir))
        self.sync_times[dir] = end_time
        self.debounced_save()
        return count

    def sync_all(self):
        count = 0
        for dir in self.sync_times.keys():
            count += self.sync_dir(dir, all=True)
        return count
